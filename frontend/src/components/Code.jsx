import React, { useState, useEffect } from 'react';

// Mock code templates based on the project idea
const CODE_TEMPLATES = {
  healthcare: {
    insurance: {
      'Claims Processing': {
        language: 'Python',
        framework: 'FastAPI',
        code: `# Claims Processing System
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

app = FastAPI(title="Claims Processing API")

class Claim(BaseModel):
    claim_id: str
    patient_id: str
    provider_id: str
    service_code: str
    amount: float
    status: str = "pending"
    submitted_date: datetime
    processed_date: Optional[datetime] = None

class ClaimProcessor:
    def __init__(self):
        self.claims_db = []
    
    def submit_claim(self, claim_data: dict) -> Claim:
        claim = Claim(
            claim_id=str(uuid.uuid4()),
            **claim_data,
            submitted_date=datetime.now()
        )
        self.claims_db.append(claim)
        return claim
    
    def process_claim(self, claim_id: str) -> Claim:
        claim = next((c for c in self.claims_db if c.claim_id == claim_id), None)
        if not claim:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        # Mock processing logic
        claim.status = "approved" if claim.amount < 1000 else "pending_review"
        claim.processed_date = datetime.now()
        return claim

processor = ClaimProcessor()

@app.post("/claims/submit")
async def submit_claim(claim_data: dict):
    """Submit a new insurance claim"""
    claim = processor.submit_claim(claim_data)
    return {"message": "Claim submitted successfully", "claim_id": claim.claim_id}

@app.get("/claims/{claim_id}")
async def get_claim(claim_id: str):
    """Get claim details by ID"""
    claim = next((c for c in processor.claims_db if c.claim_id == claim_id), None)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim

@app.post("/claims/{claim_id}/process")
async def process_claim(claim_id: str):
    """Process a submitted claim"""
    claim = processor.process_claim(claim_id)
    return {"message": "Claim processed", "status": claim.status}

@app.get("/claims")
async def list_claims():
    """List all claims"""
    return processor.claims_db

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)`
      },
      'Prior Authorization': {
        language: 'JavaScript',
        framework: 'Node.js + Express',
        code: `// Prior Authorization System
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

const app = express();
app.use(express.json());
app.use(cors());

// MongoDB Schema
const authRequestSchema = new mongoose.Schema({
  requestId: { type: String, required: true, unique: true },
  patientId: { type: String, required: true },
  providerId: { type: String, required: true },
  serviceCode: { type: String, required: true },
  diagnosisCode: { type: String, required: true },
  urgency: { type: String, enum: ['routine', 'urgent', 'stat'], default: 'routine' },
  status: { type: String, enum: ['pending', 'approved', 'denied', 'requires_info'], default: 'pending' },
  submittedAt: { type: Date, default: Date.now },
  reviewedAt: { type: Date },
  reviewerId: { type: String },
  notes: { type: String }
});

const AuthRequest = mongoose.model('AuthRequest', authRequestSchema);

// Business Logic
class PriorAuthService {
  async submitRequest(requestData) {
    const authRequest = new AuthRequest({
      requestId: this.generateRequestId(),
      ...requestData
    });
    
    await authRequest.save();
    return authRequest;
  }
  
  async reviewRequest(requestId, reviewerId, decision, notes) {
    const request = await AuthRequest.findOne({ requestId });
    if (!request) {
      throw new Error('Request not found');
    }
    
    request.status = decision;
    request.reviewedAt = new Date();
    request.reviewerId = reviewerId;
    request.notes = notes;
    
    await request.save();
    return request;
  }
  
  generateRequestId() {
    return 'PA' + Date.now() + Math.random().toString(36).substr(2, 5);
  }
}

const authService = new PriorAuthService();

// API Routes
app.post('/api/auth-requests', async (req, res) => {
  try {
    const request = await authService.submitRequest(req.body);
    res.status(201).json({
      success: true,
      message: 'Prior authorization request submitted',
      requestId: request.requestId
    });
  } catch (error) {
    res.status(400).json({ success: false, error: error.message });
  }
});

app.get('/api/auth-requests/:requestId', async (req, res) => {
  try {
    const request = await AuthRequest.findOne({ requestId: req.params.requestId });
    if (!request) {
      return res.status(404).json({ success: false, error: 'Request not found' });
    }
    res.json({ success: true, data: request });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.post('/api/auth-requests/:requestId/review', async (req, res) => {
  try {
    const { reviewerId, decision, notes } = req.body;
    const request = await authService.reviewRequest(req.params.requestId, reviewerId, decision, notes);
    res.json({
      success: true,
      message: 'Request reviewed successfully',
      data: request
    });
  } catch (error) {
    res.status(400).json({ success: false, error: error.message });
  }
});

app.get('/api/auth-requests', async (req, res) => {
  try {
    const { status, providerId } = req.query;
    const filter = {};
    if (status) filter.status = status;
    if (providerId) filter.providerId = providerId;
    
    const requests = await AuthRequest.find(filter).sort({ submittedAt: -1 });
    res.json({ success: true, data: requests });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(\`Prior Authorization API running on port \${PORT}\`);
});`
      }
    }
  },
  fintech: {
    payments: {
      'Mobile Payments': {
        language: 'Python',
        framework: 'Django',
        code: `# Mobile Payment System
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
import uuid
from datetime import datetime

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='USD')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('transfer', 'Transfer'),
        ('payment', 'Payment'),
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_transactions')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

class PaymentService:
    def __init__(self):
        self.minimum_amount = Decimal('0.01')
        self.maximum_amount = Decimal('10000.00')
    
    def process_payment(self, sender_id, recipient_id, amount, description=''):
        try:
            sender = User.objects.get(id=sender_id)
            recipient = User.objects.get(id=recipient_id)
            
            # Validate amount
            if amount < self.minimum_amount or amount > self.maximum_amount:
                raise ValueError("Amount out of allowed range")
            
            # Check sender balance
            sender_wallet = Wallet.objects.get(user=sender)
            if sender_wallet.balance < amount:
                raise ValueError("Insufficient funds")
            
            # Create transaction
            transaction = Transaction.objects.create(
                sender=sender,
                recipient=recipient,
                amount=amount,
                transaction_type='payment',
                description=description
            )
            
            # Process payment
            sender_wallet.balance -= amount
            sender_wallet.save()
            
            recipient_wallet, created = Wallet.objects.get_or_create(user=recipient)
            recipient_wallet.balance += amount
            recipient_wallet.save()
            
            transaction.status = 'completed'
            transaction.completed_at = datetime.now()
            transaction.save()
            
            return transaction
            
        except Exception as e:
            if 'transaction' in locals():
                transaction.status = 'failed'
                transaction.save()
            raise e

# API Views
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import TransactionSerializer

@api_view(['POST'])
def send_payment(request):
    """Send a payment to another user"""
    serializer = TransactionSerializer(data=request.data)
    if serializer.is_valid():
        try:
            payment_service = PaymentService()
            transaction = payment_service.process_payment(
                sender_id=request.user.id,
                recipient_id=serializer.validated_data['recipient_id'],
                amount=serializer.validated_data['amount'],
                description=serializer.validated_data.get('description', '')
            )
            return Response({
                'success': True,
                'transaction_id': str(transaction.transaction_id),
                'status': transaction.status
            }, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def transaction_history(request):
    """Get user's transaction history"""
    transactions = Transaction.objects.filter(
        models.Q(sender=request.user) | models.Q(recipient=request.user)
    ).order_by('-created_at')
    
    serializer = TransactionSerializer(transactions, many=True)
    return Response({
        'success': True,
        'transactions': serializer.data
    })`
      }
    }
  },
  ecommerce: {
    marketplace: {
      'Product Catalog': {
        language: 'React + Node.js',
        framework: 'Express + MongoDB',
        code: `// Product Catalog System
const express = require('express');
const mongoose = require('mongoose');
const multer = require('multer');
const path = require('path');

const app = express();
app.use(express.json());

// Product Schema
const productSchema = new mongoose.Schema({
  name: { type: String, required: true },
  description: { type: String, required: true },
  price: { type: Number, required: true },
  category: { type: String, required: true },
  brand: { type: String, required: true },
  sku: { type: String, required: true, unique: true },
  images: [{ type: String }],
  inventory: {
    quantity: { type: Number, default: 0 },
    lowStockThreshold: { type: Number, default: 10 }
  },
  attributes: {
    color: String,
    size: String,
    weight: Number,
    dimensions: {
      length: Number,
      width: Number,
      height: Number
    }
  },
  ratings: {
    average: { type: Number, default: 0 },
    count: { type: Number, default: 0 }
  },
  seller: { type: mongoose.Schema.Types.ObjectId, ref: 'Seller', required: true },
  status: { type: String, enum: ['active', 'inactive', 'discontinued'], default: 'active' },
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
});

const Product = mongoose.model('Product', productSchema);

// Seller Schema
const sellerSchema = new mongoose.Schema({
  name: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  businessType: { type: String, required: true },
  rating: { type: Number, default: 0 },
  isVerified: { type: Boolean, default: false }
});

const Seller = mongoose.model('Seller', sellerSchema);

// Product Service
class ProductService {
  async createProduct(productData, sellerId) {
    const seller = await Seller.findById(sellerId);
    if (!seller) {
      throw new Error('Seller not found');
    }
    
    const product = new Product({
      ...productData,
      seller: sellerId
    });
    
    await product.save();
    return product;
  }
  
  async searchProducts(query, filters = {}) {
    const searchCriteria = {};
    
    if (query) {
      searchCriteria.$or = [
        { name: { $regex: query, $options: 'i' } },
        { description: { $regex: query, $options: 'i' } },
        { brand: { $regex: query, $options: 'i' } }
      ];
    }
    
    if (filters.category) {
      searchCriteria.category = filters.category;
    }
    
    if (filters.minPrice || filters.maxPrice) {
      searchCriteria.price = {};
      if (filters.minPrice) searchCriteria.price.$gte = filters.minPrice;
      if (filters.maxPrice) searchCriteria.price.$lte = filters.maxPrice;
    }
    
    if (filters.brand) {
      searchCriteria.brand = filters.brand;
    }
    
    const products = await Product.find(searchCriteria)
      .populate('seller', 'name rating isVerified')
      .sort({ createdAt: -1 });
    
    return products;
  }
  
  async updateInventory(productId, quantity) {
    const product = await Product.findById(productId);
    if (!product) {
      throw new Error('Product not found');
    }
    
    product.inventory.quantity = quantity;
    product.updatedAt = new Date();
    
    await product.save();
    return product;
  }
}

const productService = new ProductService();

// API Routes
app.post('/api/products', async (req, res) => {
  try {
    const { sellerId, ...productData } = req.body;
    const product = await productService.createProduct(productData, sellerId);
    res.status(201).json({
      success: true,
      message: 'Product created successfully',
      product
    });
  } catch (error) {
    res.status(400).json({ success: false, error: error.message });
  }
});

app.get('/api/products/search', async (req, res) => {
  try {
    const { q, category, minPrice, maxPrice, brand } = req.query;
    const products = await productService.searchProducts(q, {
      category,
      minPrice: minPrice ? parseFloat(minPrice) : undefined,
      maxPrice: maxPrice ? parseFloat(maxPrice) : undefined,
      brand
    });
    
    res.json({
      success: true,
      count: products.length,
      products
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.get('/api/products/:id', async (req, res) => {
  try {
    const product = await Product.findById(req.params.id)
      .populate('seller', 'name rating isVerified');
    
    if (!product) {
      return res.status(404).json({ success: false, error: 'Product not found' });
    }
    
    res.json({ success: true, product });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.put('/api/products/:id/inventory', async (req, res) => {
  try {
    const { quantity } = req.body;
    const product = await productService.updateInventory(req.params.id, quantity);
    res.json({
      success: true,
      message: 'Inventory updated successfully',
      product
    });
  } catch (error) {
    res.status(400).json({ success: false, error: error.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(\`Product Catalog API running on port \${PORT}\`);
});`
      }
    }
  }
};

function Code({ onComplete, projectData }) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedCode, setGeneratedCode] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState('');
  const [selectedFramework, setSelectedFramework] = useState('');

  useEffect(() => {
    // Simulate code generation based on project data
    if (projectData.niche && projectData.subNiche && projectData.specificArea) {
      generateCode();
    }
  }, [projectData]);

  const generateCode = async () => {
    setIsGenerating(true);
    
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Get template based on project data
    const template = CODE_TEMPLATES[projectData.niche]?.[projectData.subNiche]?.[projectData.specificArea];
    
    if (template) {
      setGeneratedCode(template.code);
      setSelectedLanguage(template.language);
      setSelectedFramework(template.framework);
    } else {
      // Fallback generic template
      setGeneratedCode(`// ${projectData.specificArea} Implementation
// Generated for: ${projectData.idea}

class ${projectData.specificArea.replace(/\s+/g, '')}Service {
  constructor() {
    this.initialized = true;
  }
  
  async processRequest(data) {
    // Implementation for ${projectData.specificArea}
    console.log('Processing request:', data);
    return { success: true, data };
  }
  
  async validateInput(input) {
    // Input validation logic
    if (!input) {
      throw new Error('Invalid input provided');
    }
    return true;
  }
}

module.exports = ${projectData.specificArea.replace(/\s+/g, '')}Service;`);
      setSelectedLanguage('JavaScript');
      setSelectedFramework('Node.js');
    }
    
    setIsGenerating(false);
    
    // Automatically proceed to debugging after code generation
    setTimeout(() => {
      handleContinue();
    }, 2000);
  };

  const handleContinue = () => {
    onComplete({
      generatedCode,
      language: selectedLanguage,
      framework: selectedFramework
    });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">


      {isGenerating ? (
        <div className="flex flex-col items-center justify-center py-16">
          <div className="relative mb-8">
            <div className="w-24 h-24 border-4 border-[#343434] border-t-white rounded-full animate-spin"></div>
          </div>
          <h3 className="text-2xl font-semibold text-white mb-2">Generating Code...</h3>
        </div>
      ) : (
        <div className="space-y-8">
          {/* Generation Results */}
          <div className=" rounded-lg pt-16 text-center">
            <div className="mb-16">
              <div className="text-6xl font-bold text-white mb-2">✓</div>
              <div className="text-[16px] text-[#888888]">Code Generated Successfully</div>
            </div>
            
            <div className="grid grid-cols-2 gap-6">
              <div>
                <div className="text-2xl font-medium text-white mb-1">{selectedLanguage}</div>
                <div className="text-md text-[#888888]">Programming Language</div>
              </div>
              <div>
                <div className="text-2xl font-medium text-white mb-1">{selectedFramework}</div>
                <div className="text-md text-[#888888]">Framework</div>
              </div>
            </div>

            <div className="mt-16">
              <div className="inline-flex items-center space-x-2 px-6 py-3 bg-white text-[#121212] rounded-lg">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-[#121212]"></div>
                <span className="font-semibold">Proceeding to debugging...</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Code;
