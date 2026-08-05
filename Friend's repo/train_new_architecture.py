import os
import time
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from collections import Counter
from tqdm import tqdm

# ==========================================
# ⚙️ CONFIGURATION FOR THE NEW ARCHITECTURE
# ==========================================
DATA_DIR = "data/HAM10000_Sorted-20260803T132100Z-1-001/HAM10000_Sorted"
NEW_MODEL_SAVE_PATH = "models/dermascan_densenet_model.pth"

BATCH_SIZE = 8 # Lowered from 32 to 8 for RTX 3050 6GB VRAM
LEARNING_RATE = 1e-4
TARGET_ACCURACY = 95.0
MAX_EPOCHS = 200
PATIENCE = 15

# ==========================================
# 🧠 THE COMPLETELY NEW MODEL ARCHITECTURE
# ==========================================
class DermaScanDenseNet(nn.Module):
    """
    Instead of EfficientNet, we are using DenseNet-121!
    Why DenseNet? DenseNet connects every layer to every other layer. 
    In medical imaging (like dermoscopy), this is famous for passing tiny, 
    low-level details (like edges and colors) all the way to the final decision layer.
    """
    def __init__(self, num_classes=7, freeze_base=True):
        super(DermaScanDenseNet, self).__init__()
        
        # Load pre-trained DenseNet121
        self.base_model = models.densenet121(weights='IMAGENET1K_V1')
        
        if freeze_base:
            for param in self.base_model.parameters():
                param.requires_grad = False
                
        # Replace the classifier for our specific number of skin lesion classes
        num_features = self.base_model.classifier.in_features
        
        self.base_model.classifier = nn.Sequential(
            nn.Linear(num_features, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(512, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes)
        )
        
    def forward(self, x):
        return self.base_model(x)

# ==========================================
# 🛠️ DATA PREPARATION (Automatic Train/Val Split)
# ==========================================
def get_data_loaders():
    # If the user has a single folder with class subfolders (like 'akiec', 'bcc'), 
    # we load it all and split it automatically!
    if not os.path.exists(DATA_DIR):
        print(f"❌ Error: Could not find the dataset at {DATA_DIR}. Please update DATA_DIR on line 13!")
        return None, None, None

    # Load the entire dataset
    # Note: We apply training augmentations here. Validation will technically get them too, 
    # which is fine for a quick setup, but usually val uses only resize/normalize.
    base_transforms = transforms.Compose([
        transforms.Resize((380, 380)),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # Check if the user has 'train' and 'val' subfolders inside DATA_DIR
    if os.path.exists(os.path.join(DATA_DIR, 'train')):
        print("📂 Found 'train' and 'val' folders! Loading normally...")
        train_dataset = datasets.ImageFolder(os.path.join(DATA_DIR, 'train'), transform=base_transforms)
        val_dataset = datasets.ImageFolder(os.path.join(DATA_DIR, 'val'), transform=transforms.Compose([transforms.Resize((380,380)), transforms.ToTensor(), transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])]))
    else:
        print("📂 No 'train' folder found. Automatically splitting your dataset (80% train, 20% val)...")
        full_dataset = datasets.ImageFolder(DATA_DIR, transform=base_transforms)
        
        train_size = int(0.8 * len(full_dataset))
        val_size = len(full_dataset) - train_size
        train_dataset, val_dataset = torch.utils.data.random_split(full_dataset, [train_size, val_size])
        
        # We need to attach the classes attribute to the split datasets for our class weight function
        train_dataset.classes = full_dataset.classes
        train_dataset.targets = [full_dataset.targets[i] for i in train_dataset.indices]
        val_dataset.classes = full_dataset.classes

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0, drop_last=True) # drop_last prevents BatchNorm crash on final batch
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    return train_loader, val_loader, train_dataset

def calculate_class_weights(dataset):
    class_counts = dict(Counter(dataset.targets))
    total = sum(class_counts.values())
    weights = [total / (len(dataset.classes) * class_counts.get(i, 1)) for i in range(len(dataset.classes))]
    return torch.FloatTensor(weights)

# ==========================================
# 🚀 MAIN TRAINING LOOP FOR NEW ARCHITECTURE
# ==========================================
def train_new_architecture():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🔥 Training NEW Architecture on device: {device}")

    train_loader, val_loader, train_dataset = get_data_loaders()
    if train_loader is None:
        return
        
    num_classes = len(train_dataset.classes)
    print(f"📊 Found {num_classes} classes: {train_dataset.classes}")

    # 1. Initialize the COMPLETELY NEW DenseNet model
    # We set freeze_base=False right away to train the whole thing since it's a new model for this data
    model = DermaScanDenseNet(num_classes=num_classes, freeze_base=False).to(device)

    # 2. Use the Anti-Lazy Class Weights
    class_weights = calculate_class_weights(train_dataset).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE, weight_decay=1e-5)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=5)

    best_acc = 0.0
    epochs_no_improve = 0

    os.makedirs(os.path.dirname(NEW_MODEL_SAVE_PATH), exist_ok=True)
    print(f"🎯 Target Accuracy set to {TARGET_ACCURACY}%. Training DenseNet-121 from scratch (transfer learning)...")
    
    for epoch in range(1, MAX_EPOCHS + 1):
        start_time = time.time()
        
        # --- TRAINING PHASE ---
        model.train()
        running_loss = 0.0
        correct = 0; total = 0

        print(f"\\nEpoch {epoch}/{MAX_EPOCHS}")
        train_pbar = tqdm(train_loader, desc="Training")
        for inputs, labels in train_pbar:
            inputs, labels = inputs.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * inputs.size(0)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
            # Update progress bar text dynamically
            train_pbar.set_postfix({'loss': running_loss/total, 'acc': 100 * correct / total})

        train_loss = running_loss / total
        train_acc = 100 * correct / total

        # --- VALIDATION PHASE ---
        model.eval()
        val_loss = 0.0
        val_correct = 0; val_total = 0

        val_pbar = tqdm(val_loader, desc="Validating")
        with torch.no_grad():
            for inputs, labels in val_pbar:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)

                val_loss += loss.item() * inputs.size(0)
                _, predicted = torch.max(outputs, 1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()
                
                val_pbar.set_postfix({'val_loss': val_loss/val_total, 'val_acc': 100 * val_correct / val_total})

        val_loss = val_loss / val_total
        val_acc = 100 * val_correct / val_total
        
        epoch_time = time.time() - start_time
        print(f"Epoch {epoch}/{MAX_EPOCHS} [{epoch_time:.0f}s] "
              f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}% | "
              f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2f}%")

        scheduler.step(val_acc)

        if val_acc > best_acc:
            print(f"⭐ New DenseNet record! {best_acc:.2f}% -> {val_acc:.2f}%. Saving...")
            best_acc = val_acc
            torch.save(model.state_dict(), NEW_MODEL_SAVE_PATH)
            epochs_no_improve = 0
        else:
            epochs_no_improve += 1

        if best_acc >= TARGET_ACCURACY:
            print(f"🏆 Target reached! Stopping training.")
            break
            
        if epochs_no_improve >= PATIENCE:
            print(f"⚠️ Early stopping. No improvement for {PATIENCE} epochs.")
            break

    print(f"✅ Training complete! Model saved to {NEW_MODEL_SAVE_PATH}")

if __name__ == "__main__":
    train_new_architecture()
