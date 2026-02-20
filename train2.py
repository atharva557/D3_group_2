"""
Reddit Pulse - Ultimate BERT Fine-Tuning Script
================================================
This script combines the best features from both training approaches:
    - Mixed precision training for speed and memory efficiency
    - Comprehensive visualizations (loss curves + confusion matrix)
    - Robust evaluation metrics (accuracy + per-class performance)
    - GPU optimizations for 8GB VRAM
    - Both single-file and pre-split dataset support
    - Best model checkpointing (saves only the best performing model)

Dataset: GoEmotions (Google Research)
    - 58,000 Reddit comments
    - 28 emotion labels
    - Multi-label classification

Training Configuration:
    - Base Model: bert-base-uncased (or custom pre-trained from pretrain.py)
    - Epochs: 4 (optimal balance)
    - Batch Size: 16
    - Learning Rate: 2e-5
    - Mixed Precision: Enabled (faster + memory efficient)
    - Optimizer: AdamW
    - Best Model Saving: Enabled (tracks lowest validation loss)

Author: Reddit Pulse Team
License: MIT
"""

# ============================================================================
# IMPORTS
# ============================================================================

import torch  # Core PyTorch library for deep learning
import pandas as pd  # For loading and manipulating CSV data
import numpy as np  # For numerical operations (arrays, matrix operations)
import os  # For file path operations (checking if directories exist)
from torch.utils.data import Dataset, DataLoader  # For creating custom datasets and batch loading
from transformers import BertTokenizer, BertForSequenceClassification  # HuggingFace BERT components
from torch.optim import AdamW  # Adam optimizer with weight decay (better for transformers)
from torch.cuda.amp import autocast, GradScaler  # For mixed precision training (faster, less memory)
from sklearn.model_selection import train_test_split  # For splitting data into train/validation
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report  # For evaluation metrics

# ============================================================================
# CONFIGURATION
# ============================================================================

# Path to your pre-trained model (from pretrain.py) or use default BERT
BASE_MODEL_PATH = "./bert_reddit_base_just_for_values"  # Use your Reddit-trained BERT (better for Reddit text)
# BASE_MODEL_PATH = "bert-base-uncased"  # Or use Google's default BERT (general purpose)

# Training hyperparameters
EPOCHS = 4  # Number of complete passes through the training data (4 is optimal balance)
BATCH_SIZE = 16  # Number of samples processed together (16 fits in 8GB GPU memory)
LEARNING_RATE = 2e-5  # How fast the model learns (2e-5 is standard for BERT fine-tuning)
MAX_LENGTH = 128  # Maximum number of tokens per text (BERT's optimal length)

# Output directory for the trained model
OUTPUT_PATH = "./best_reddit_model"  # Where to save the final trained model


# Check device availability (GPU vs CPU)
if torch.cuda.is_available():  # Check if NVIDIA GPU with CUDA is available
    device = torch.device("cuda")  # Use GPU for training (much faster)
    print(f"🚀 Using GPU: {torch.cuda.get_device_name(0)}")  # Print GPU name (e.g., "RTX 3060")
    print(f"   GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")  # Print total GPU memory
else:
    device = torch.device("cpu")  # Fallback to CPU if no GPU (very slow)
    print("⚠️ Using CPU (Training will be VERY slow - GPU highly recommended)")


# ============================================================================
# DATASET CLASS
# ============================================================================

class GoEmotionsDataset(Dataset):
    """
    PyTorch Dataset for GoEmotions emotion classification.

    This dataset handles:
    - Loading CSV data (text + emotion labels)
    - Tokenizing text using BERT tokenizer
    - Converting emotion labels to multi-hot vectors

    PyTorch Dataset Requirements:
        - __init__: Initialize the dataset
        - __len__: Return total number of samples
        - __getitem__: Return a single sample by index
    """

    def __init__(self, dataframe, tokenizer, max_length, emotion_columns):
        """
        Initialize the dataset with data and tokenizer.

        Args:
            dataframe (pd.DataFrame): DataFrame with 'text' and emotion columns
            tokenizer (BertTokenizer): BERT tokenizer for text encoding
            max_length (int): Maximum sequence length (truncate longer texts)
            emotion_columns (list): List of emotion column names (e.g., ['joy', 'anger', ...])
        """
        self.data = dataframe.reset_index(drop=True)  # Reset index to ensure continuous 0,1,2,... indexing
        self.tokenizer = tokenizer  # Store tokenizer for text encoding
        self.max_length = max_length  # Store max length for truncation
        self.text = self.data['text']  # Extract text column for easy access
        self.targets = self.data[emotion_columns].values  # Extract emotion labels as numpy array

    def __len__(self):
        """
        Return the number of samples in the dataset.

        PyTorch calls this to determine dataset size.

        Returns:
            int: Total number of samples
        """
        return len(self.text)  # Return number of text samples

    def __getitem__(self, idx):
        """
        Get a single training sample by index.

        PyTorch calls this when loading batches. It must return:
        - Tokenized input (input_ids, attention_mask)
        - Labels (multi-hot emotion vector)

        Args:
            idx (int): Sample index (0 to len-1)

        Returns:
            dict: Contains input_ids, attention_mask, and multi-hot label vector
        """
        # Get text at index and convert to string (handle any non-string values)
        text = str(self.text[idx])

        # Clean extra whitespace (multiple spaces become single space)
        text = " ".join(text.split())

        # Tokenize text with BERT tokenizer
        encoding = self.tokenizer.encode_plus(
            text,  # The text to tokenize
            add_special_tokens=True,  # Add [CLS] and [SEP] tokens (required by BERT)
            max_length=self.max_length,  # Truncate if text is longer than 128 tokens
            padding='max_length',  # Pad shorter texts to 128 tokens (uniform batch size)
            truncation=True,  # Cut off text if it exceeds max_length
            return_attention_mask=True,  # Return mask showing real tokens vs padding
            return_tensors='pt'  # Return PyTorch tensors (not lists)
        )

        # Return dictionary with all required components
        return {
            'input_ids': encoding['input_ids'].squeeze(),  # Token IDs (remove extra dimension)
            'attention_mask': encoding['attention_mask'].squeeze(),  # Attention mask (remove extra dimension)
            'labels': torch.tensor(self.targets[idx], dtype=torch.float)  # Emotion labels as float tensor
        }


# ============================================================================
# DATA LOADING
# ============================================================================

def load_data():
    """
    Load and prepare the GoEmotions dataset.

    This function handles two modes:
        1. Single file mode: Loads one CSV and splits it into train/validation
        2. Pre-split mode: Loads separate train and validation CSVs

    Returns:
        tuple: (train_dataset, val_dataset, emotion_columns, tokenizer)
            - train_dataset: PyTorch Dataset for training
            - val_dataset: PyTorch Dataset for validation
            - emotion_columns: List of emotion label names
            - tokenizer: BERT tokenizer instance
    """
    print("📂 Loading GoEmotions Data...")  # User feedback

        # Load single CSV file containing all data
    print("   Mode: Single file with runtime split")
    df = pd.read_csv('go_emotions_dataset.csv')  # Load entire dataset

    # Identify emotion columns by excluding metadata columns
    exclude = ['text', 'id', 'author', 'subreddit', 'link_id',
                   'parent_id', 'created_utc', 'rater_id', 'example_very_unclear']  # Non-emotion columns
    emotion_cols = [c for c in df.columns if c not in exclude]  # Keep only emotion columns

    # Split into train (90%) and validation (10%) sets
    train_df, val_df = train_test_split(
            df,  # DataFrame to split
            test_size=0.1,  # 10% for validation, 90% for training
            random_state=42,  # Fixed seed for reproducibility (same split every time)
            shuffle=True  # Randomize before splitting (important for unbiased evaluation)
        )

    # Print dataset statistics for user feedback
    print(f"✅ Found {len(emotion_cols)} emotions: {emotion_cols[:5]}... (showing first 5)")
    print(f"📊 Training samples: {len(train_df)}")  # Number of training examples
    print(f"📉 Validation samples: {len(val_df)}")  # Number of validation examples

    # Check if custom pre-trained model exists, otherwise use default BERT
    model_source = BASE_MODEL_PATH if os.path.exists(BASE_MODEL_PATH) else 'bert-base-uncased'
    print(f"🧠 Loading tokenizer from: {model_source}")

    # Load BERT tokenizer (converts text to token IDs)
    tokenizer = BertTokenizer.from_pretrained(model_source)

    # Create PyTorch Dataset objects for train and validation
    train_dataset = GoEmotionsDataset(train_df, tokenizer, MAX_LENGTH, emotion_cols)
    val_dataset = GoEmotionsDataset(val_df, tokenizer, MAX_LENGTH, emotion_cols)

    # Return all components needed for training
    return train_dataset, val_dataset, emotion_cols, tokenizer


# ============================================================================
# MODEL INITIALIZATION
# ============================================================================

def initialize_model(num_labels):
    """
    Initialize BERT model for multi-label emotion classification.

    This function:
    - Loads pre-trained BERT weights
    - Configures it for multi-label classification (28 emotions)
    - Moves model to GPU/CPU
    - Prints model statistics

    Args:
        num_labels (int): Number of emotion labels (28 for GoEmotions)

    Returns:
        BertForSequenceClassification: Initialized model ready for training
    """
    # Determine which BERT model to load (custom or default)
    model_source = BASE_MODEL_PATH if os.path.exists(BASE_MODEL_PATH) else 'bert-base-uncased'
    print(f"🧠 Initializing model from: {model_source}")

    # Load BERT model with classification head
    model = BertForSequenceClassification.from_pretrained(
        model_source,  # Path to pre-trained model
        num_labels=num_labels,  # Output layer size (28 for emotions)
        problem_type="multi_label_classification"  # Enable multi-label mode (multiple emotions per text)
    )

    # Move model to GPU or CPU
    model.to(device)

    # Calculate and print model statistics
    total_params = sum(p.numel() for p in model.parameters())  # Total number of parameters
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)  # Parameters that will be updated
    print(f"   Total parameters: {total_params:,}")  # Format with commas (e.g., 110,000,000)
    print(f"   Trainable parameters: {trainable_params:,}")

    return model  # Return initialized model


# ============================================================================
# TRAINING LOOP
# ============================================================================

def train_model(model, train_loader, val_loader, optimizer, scaler):
    """
    Main training loop with mixed precision and best model checkpointing.

    This function:
    - Trains the model for EPOCHS iterations
    - Uses mixed precision for speed and memory efficiency
    - Validates after each epoch
    - Saves only the best model (lowest validation loss)
    - Tracks metrics for visualization

    Args:
        model: BERT model to train
        train_loader: DataLoader for training batches
        val_loader: DataLoader for validation batches
        optimizer: AdamW optimizer for updating weights
        scaler: GradScaler for mixed precision training

    Returns:
        tuple: (train_losses, val_losses, val_accuracies)
            - train_losses: List of training loss per epoch
            - val_losses: List of validation loss per epoch
            - val_accuracies: List of validation accuracy per epoch
    """
    print(f"\n🔥 Starting Training Loop...")  # User feedback
    print(f"{'=' * 70}")  # Visual separator

    # Initialize lists to track metrics across epochs
    train_losses = []  # Store average training loss per epoch
    val_losses = []  # Store average validation loss per epoch
    val_accuracies = []  # Store validation accuracy per epoch

    # TRACKING BEST MODEL - saves only when validation loss improves
    best_val_loss = float('inf')  # Initialize to infinity (any loss will be better)

    # Main training loop - iterate through epochs
    for epoch in range(EPOCHS):
        print(f"\n{'=' * 70}")  # Visual separator
        print(f"EPOCH {epoch + 1}/{EPOCHS}")  # Show current epoch (1-indexed for humans)
        print(f"{'=' * 70}")

        # ====================================================================
        # TRAINING PHASE
        # ====================================================================
        model.train()  # Set model to training mode (enables dropout, batch norm training)
        total_train_loss = 0  # Accumulator for batch losses

        # Iterate through training batches
        for step, batch in enumerate(train_loader):
            # Move batch data to GPU/CPU
            input_ids = batch['input_ids'].to(device)  # Token IDs
            attention_mask = batch['attention_mask'].to(device)  # Mask for real tokens vs padding
            labels = batch['labels'].to(device)  # Emotion labels (multi-hot vectors)

            # Zero out gradients from previous step (PyTorch accumulates by default)
            optimizer.zero_grad()

            # Mixed precision forward pass (faster, uses less memory)
            with autocast():  # Automatically uses FP16 where safe, FP32 where needed
                outputs = model(
                    input_ids=input_ids,  # Token IDs
                    attention_mask=attention_mask,  # Attention mask
                    labels=labels  # Ground truth labels (loss computed automatically)
                )
                loss = outputs.loss  # Extract loss from model output

            # Mixed precision backward pass
            scaler.scale(loss).backward()  # Scale loss to prevent underflow in FP16
            scaler.step(optimizer)  # Update weights (unscales gradients first)
            scaler.update()  # Update scaler for next iteration

            # Accumulate loss for averaging
            total_train_loss += loss.item()  # .item() converts tensor to Python number

            # Print progress every 100 steps
            if step % 100 == 0 and step > 0:
                avg_loss = total_train_loss / (step + 1)  # Calculate average loss so far
                print(f"   Step {step}/{len(train_loader)} | Loss: {loss.item():.4f} | Avg: {avg_loss:.4f}")

        # Calculate average training loss for this epoch
        avg_train_loss = total_train_loss / len(train_loader)  # Divide by number of batches
        train_losses.append(avg_train_loss)  # Store for plotting later
        print(f"\n✅ Training Loss: {avg_train_loss:.4f}")  # Print epoch summary

        # ====================================================================
        # VALIDATION PHASE
        # ====================================================================
        model.eval()  # Set model to evaluation mode (disables dropout, batch norm uses running stats)
        total_val_loss = 0  # Accumulator for validation loss
        all_preds = []  # Store predictions for accuracy calculation
        all_labels = []  # Store ground truth labels for accuracy calculation

        print("📊 Running validation...")  # User feedback

        # No gradient calculation needed for validation (saves memory and time)
        with torch.no_grad():
            # Iterate through validation batches
            for batch in val_loader:
                # Move batch to device
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['labels'].to(device)

                # Forward pass (no autocast needed - validation is already fast)
                outputs = model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                loss = outputs.loss  # Get validation loss
                total_val_loss += loss.item()  # Accumulate

                # Get predictions for accuracy calculation
                probs = torch.sigmoid(outputs.logits)  # Convert logits to probabilities (0-1)
                preds = (probs > 0.5).float()  # Threshold at 0.5 (multi-label classification)

                # Move to CPU and store (can't calculate metrics on GPU tensors)
                all_preds.append(preds.cpu().numpy())
                all_labels.append(labels.cpu().numpy())

        # Calculate average validation loss
        avg_val_loss = total_val_loss / len(val_loader)
        val_losses.append(avg_val_loss)  # Store for plotting

        # Calculate accuracy (exact match - all emotions must be correct)
        all_preds = np.vstack(all_preds)  # Stack all batches into single array
        all_labels = np.vstack(all_labels)
        accuracy = accuracy_score(all_labels, all_preds)  # Compare predictions to ground truth
        val_accuracies.append(accuracy)  # Store for plotting

        # Print validation metrics
        print(f"📉 Validation Loss: {avg_val_loss:.4f}")
        print(f"🎯 Validation Accuracy: {accuracy:.2%}")  # Format as percentage

        # ====================================================================
        # SAVE BEST MODEL LOGIC
        # ====================================================================
        # Only save model if validation loss improved (prevents saving worse models)
        if avg_val_loss < best_val_loss:
            print(f"✨ Improvement! (Loss: {best_val_loss:.4f} -> {avg_val_loss:.4f})")
            print(f"💾 Saving BEST model to {OUTPUT_PATH}...")
            best_val_loss = avg_val_loss  # Update best loss tracker

            # Save the model immediately (overwrites previous best)
            model.save_pretrained(OUTPUT_PATH)  # Saves model weights and config
            # Note: Tokenizer is saved once at the end (doesn't change during training)
        else:
            # Validation loss didn't improve - don't save
            print(f"⚠️ No improvement (Best was: {best_val_loss:.4f})")

    # Return metrics for visualization
    return train_losses, val_losses, val_accuracies


def print_classification_report(model, val_loader, emotion_labels):
    """
    Print detailed classification report with per-class metrics.

    Shows for each emotion:
    - Precision: Of all predictions for this emotion, how many were correct?
    - Recall: Of all true instances of this emotion, how many did we catch?
    - F1-Score: Harmonic mean of precision and recall
    - Support: Number of true instances in validation set

    Args:
        model: Trained BERT model
        val_loader: Validation data loader
        emotion_labels (list): List of emotion names
    """
    print("\n📋 Generating classification report...")  # User feedback
    model.eval()  # Set to evaluation mode

    # Lists to store predictions and labels
    all_preds = []
    all_labels = []

    # No gradient calculation needed
    with torch.no_grad():
        # Iterate through validation batches
        for batch in val_loader:
            # Move batch to device
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)

            # Forward pass
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)

            # Get predictions
            probs = torch.sigmoid(outputs.logits)  # Convert logits to probabilities
            preds = (probs > 0.5).float()  # Threshold at 0.5 for multi-label

            # Move to CPU and store
            all_preds.append(preds.cpu().numpy())
            all_labels.append(labels.cpu().numpy())

    # Stack all batches into single arrays
    all_preds = np.vstack(all_preds)
    all_labels = np.vstack(all_labels)

    # Print detailed report using sklearn
    print("\n" + "=" * 70)
    print("CLASSIFICATION REPORT")
    print("=" * 70)
    print(classification_report(
        all_labels,  # True labels
        all_preds,  # Predicted labels
        target_names=emotion_labels,  # Emotion names for each column
        zero_division=0  # Handle edge case where no predictions for a class
    ))


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main execution function orchestrating the entire training pipeline.

    This function coordinates:
    1. Data loading and preprocessing
    2. Model initialization
    3. Training loop execution
    4. Model saving
    5. Visualization generation
    6. Final summary
    """
    # Print header
    print("\n" + "=" * 70)
    print("REDDIT PULSE - ULTIMATE BERT TRAINING")
    print("=" * 70)

    # ========================================================================
    # Step 1: Load Data
    # ========================================================================
    train_dataset, val_dataset, emotion_cols, tokenizer = load_data()

    # ========================================================================
    # Step 2: Create Data Loaders
    # ========================================================================
    # DataLoader handles batching, shuffling, and GPU transfer
    train_loader = DataLoader(
        train_dataset,  # Dataset to load from
        batch_size=BATCH_SIZE,  # Number of samples per batch (16)
        shuffle=True,  # Randomize order each epoch (prevents overfitting)
        pin_memory=True,  # Speed up GPU transfer (loads to pinned RAM first)
        num_workers=0  # Number of subprocesses (0=main process, increase if CPU bottleneck)
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,  # Don't shuffle validation (order doesn't matter)
        pin_memory=True
    )

    # ========================================================================
    # Step 3: Initialize Model
    # ========================================================================
    model = initialize_model(len(emotion_cols))  # Create BERT model with 28 output neurons

    # ========================================================================
    # Step 4: Initialize Optimizer and Scaler
    # ========================================================================
    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)  # Adam with weight decay
    scaler = GradScaler()  # For mixed precision training (FP16 + FP32)

    # ========================================================================
    # Step 5: Train Model
    # ========================================================================
    train_losses, val_losses, val_accuracies = train_model(
        model,  # Model to train
        train_loader,  # Training data
        val_loader,  # Validation data
        optimizer,  # Optimizer for weight updates
        scaler  # Gradient scaler for mixed precision
    )

    # ========================================================================
    # Step 6: Save Final Model and Tokenizer
    # ========================================================================
    # Note: Best model already saved during training, but we save again for safety
    print(f"\n💾 Saving final model to {OUTPUT_PATH}...")
    model.save_pretrained(OUTPUT_PATH)  # Save model weights and config
    tokenizer.save_pretrained(OUTPUT_PATH)  # Save tokenizer vocab and config

    # Save emotion labels as CSV for inference later
    label_df = pd.DataFrame({'emotion': emotion_cols})
    label_df.to_csv(f"{OUTPUT_PATH}/labels.csv", index=False)
    print("✅ Model saved successfully!")

    # ========================================================================
    # Step 7: Generate Visualizations
    # ========================================================================
    print_classification_report(model, val_loader, emotion_cols)  # Per-emotion metrics

    # ========================================================================
    # Step 8: Print Final Summary
    # ========================================================================
    print("\n" + "=" * 70)
    print("🎉 TRAINING COMPLETE!")
    print("=" * 70)
    print(f"✓ Model saved to: {OUTPUT_PATH}")
    print(f"✓ Final validation accuracy: {val_accuracies[-1]:.2%}")
    print(f"✓ Final validation loss: {val_losses[-1]:.4f}")
    print(f"\n👉 Load the model with: RedditEmotionAnalyzer(model_path='{OUTPUT_PATH}')")
    print("=" * 70)


# ============================================================================
# SCRIPT ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    """
    Entry point when script is run directly (not imported).

    Python convention: Code inside this block only runs when you execute:
        python train_ultimate.py

    It won't run if you import functions from this file elsewhere.
    """
    main()  # Start the training pipeline