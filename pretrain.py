import torch
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertForMaskedLM
from torch.optim import AdamW
from transformers import DataCollatorForLanguageModeling
import os

# --- CONFIGURATION ---
# MAKE SURE THIS MATCHES YOUR TEXT FILE NAME
FILE_PATH = "reddit_titles_50k.txt"
SAVE_PATH = "./bert_reddit_base"  # This is where the 'Slang Smart' brain is saved
EPOCHS = 3
BATCH_SIZE = 8  # Low batch size to prevent crashing 8GB VRAM
LEARNING_RATE = 5e-5

# Check Device
if torch.cuda.is_available():
    device = torch.device("cuda")
    print(f"🚀 Using GPU: {torch.cuda.get_device_name(0)}")
else:
    device = torch.device("cpu")
    print("⚠️ Using CPU (Slow)")

# --- 1. LOAD TOKENIZER & MODEL ---
print("🧠 Loading standard Google BERT...")
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForMaskedLM.from_pretrained('bert-base-uncased')  # MaskedLM = Fill in the blank task
model.to(device)


# --- 2. PREPARE DATASET ---
class RedditTextDataset(Dataset):
    def __init__(self, file_path, tokenizer):
        self.lines = []
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"❌ Could not find {file_path}. Did you run the scraper?")

        with open(file_path, "r", encoding="utf-8") as f:
            # Filter: Only keep lines with 4+ words (Short titles are bad for training)
            self.lines = [line.strip() for line in f.readlines() if len(line.strip().split()) >= 4]

        print(f"📊 Loaded {len(self.lines)} valid titles for training.")
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.lines)

    def __getitem__(self, idx):
        # We don't need 'labels' here because the DataCollator creates them automatically
        return self.tokenizer.encode(
            self.lines[idx],
            max_length=128,
            truncation=True,
            return_tensors='pt'
        )[0]


dataset = RedditTextDataset(FILE_PATH, tokenizer)

# The Magic Tool: Automatically hides 15% of words for BERT to guess
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer, mlm=True, mlm_probability=0.15
)

loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, collate_fn=data_collator)
optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)

# --- 3. TRAINING LOOP WITH GRAPHING ---
print(f"🔥 Starting Pre-Training (The 'Slang' Lesson)...")
model.train()

loss_history = []  # Store numbers to plot later

for epoch in range(EPOCHS):
    total_loss = 0
    print(f"\n--- Epoch {epoch + 1}/{EPOCHS} ---")

    for step, batch in enumerate(loader):
        # Move batch to GPU
        inputs = {k: v.to(device) for k, v in batch.items()}

        optimizer.zero_grad()

        outputs = model(**inputs)
        loss = outputs.loss

        loss.backward()
        optimizer.step()

        total_loss += loss.item()

        # Track loss every 50 steps
        if step % 50 == 0 and step > 0:
            avg_loss_now = total_loss / (step + 1)
            loss_history.append(avg_loss_now)
            print(f"   Step {step} | Loss: {loss.item():.4f}")

    print(f"✅ Epoch {epoch + 1} Complete.")

# --- 4. SAVE MODEL & PLOT ---
print(f"💾 Saving your custom 'Reddit BERT' to {SAVE_PATH}...")
model.save_pretrained(SAVE_PATH)
tokenizer.save_pretrained(SAVE_PATH)
print("👉 NOW you can run train.py!")