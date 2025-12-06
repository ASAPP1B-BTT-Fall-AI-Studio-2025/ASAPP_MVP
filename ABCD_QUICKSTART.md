# ABCD Dataset Integration - Quick Start

## 🎯 What You Now Have

Your Extractify application now supports the **ABCD v1.1 dataset** with **8,034 customer service conversations**.

### Files Included
- ✅ `abcd_v1.1.json.gz` - Full dataset (35 MB compressed, 116 MB uncompressed)
- ✅ `abcd_v1.1.json` - Decompressed dataset (116 MB)
- ✅ `abcd_sample_10.json` - Test sample (10 conversations, 290 KB)
- ✅ `abcd_sample_50.json` - Medium sample (50 conversations, 1.3 MB)
- ✅ `abcd_sample_100.json` - Large sample (100 conversations, 2.7 MB)

### New Backend Capabilities
- **Automatic Format Detection**: Recognizes ABCD format with `"train"` key
- **Multi-format Support**: ABCD, JSON arrays, JSONL, and plain text
- **Smart Text Extraction**: Extracts text from `delexed` and `original` fields
- **Conversation ID Tracking**: Stores original conversation IDs in metadata
- **Bulk Processing**: Handles thousands of conversations in a single request

## 🚀 Quick Start (5 minutes)

### 1. Start Backend & Frontend
```bash
# Terminal 1 - Backend
cd backend
python3 main.py

# Terminal 2 - Frontend
npm run dev
```

### 2. Open Extractify
Go to `http://localhost:3000`

### 3. Upload ABCD Sample
- Click "Upload File with Conversation"
- Select `sample-data/abcd_sample_10.json`
- System automatically detects ABCD format
- Wait for processing (10 conversations ≈ 30 seconds)

### 4. Download Results
Click "Download Results" to get JSON with all extractions

## 📊 Dataset Statistics

| Sample | Conversations | File Size | Est. Time |
|--------|---------------|-----------|-----------|
| sample_10 | 10 | 290 KB | 30 sec |
| sample_50 | 50 | 1.3 MB | 2 min |
| sample_100 | 100 | 2.7 MB | 4 min |
| Full (v1.1) | 8,034 | 116 MB | 45 min |

## 📝 What Gets Extracted

For each conversation in the ABCD dataset:

1. **Email** - Customer contact email (e.g., cminh730@email.com)
2. **Phone** - Customer phone number (e.g., (977) 625-2661)
3. **ZIP Code** - Shipping/billing ZIP (e.g., 75227)
4. **Order ID** - Order reference number (e.g., 3348917502)

Each field includes:
- Regex-based extraction result
- LLM-based extraction result (if API available)
- Final best result
- Confidence metadata

## 🔧 Technical Details

### Backend Endpoint
```bash
POST /extract-bulk
Content-Type: application/json

{
  "text": "[JSON string of ABCD dataset]",
  "fileName": "abcd_sample_10.json"
}
```

### Response Format
```json
{
  "conversations": [
    {
      "email": "cminh730@email.com",
      "phone": "(977) 625-2661",
      "zipCode": "75227",
      "orderId": "3348917502",
      "metadata": {
        "conversation_id": 3592,
        "fileName": "abcd_sample_10.json_convo_3592",
        "extractionMethod": "hybrid",
        "regexResults": {...},
        "llmResults": {...}
      }
    }
  ],
  "total": 10,
  "format": "abcd",
  "dataset": "ABCD v1.1"
}
```

## 🧪 Test Script

Run the automated test:
```bash
python3 test_abcd_extraction.py
```

This will:
1. Check backend health
2. Test with 10 conversations
3. Test with 50 conversations
4. Save results to `*_results.json` files

## 📚 Sample Output

Example extraction from a conversation:

```
Conversation Details:
├─ Customer Name: Crystal Minh
├─ Email: cminh730@email.com
├─ Phone: (977) 625-2661
├─ ZIP Code: 75227
├─ Order ID: 3348917502
└─ Member Level: Bronze

Extraction Results:
├─ Email extracted: ✓ cminh730@email.com
├─ Phone extracted: ✓ (977) 625-2661
├─ ZIP extracted: ✓ 75227
└─ Order ID extracted: ✓ 3348917502
```

## 🎨 UI Updates

The Extractify frontend now shows:
- **Bulk Processing Badge**: "📦 Bulk Processing: X conversations processed"
- **Download Results Button**: Export all results as JSON
- **Conversation History**: Shows all processed conversations

## 🐛 Troubleshooting

### Backend won't start?
```bash
cd backend && python3 -m pip install -r requirements.txt
python3 main.py
```

### File too large?
Start with smaller samples:
- `abcd_sample_10.json` (test)
- `abcd_sample_50.json` (validate)
- Then scale up as needed

### Slow processing?
- Check backend is running: `curl http://localhost:8000/health`
- Process smaller batches
- LLM extraction is slower but more accurate
- Pure regex extraction is fastest

## 📖 Full Documentation

See `ABCD_DATASET_GUIDE.md` for complete documentation including:
- Dataset structure details
- Advanced processing options
- Performance optimization tips
- API reference
- Troubleshooting guide

## ✨ Next Steps

1. **Try It**: Upload `abcd_sample_10.json` and watch it process
2. **Validate**: Check extraction quality in downloaded JSON
3. **Scale**: Try larger samples (50, 100 conversations)
4. **Optimize**: Fine-tune regex patterns if needed
5. **Deploy**: Use for production data extraction

---

**Version**: Extractify v1.0 + ABCD v1.1  
**Last Updated**: December 6, 2025  
**Status**: ✅ Ready to Use
