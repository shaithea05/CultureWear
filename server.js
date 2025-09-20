// server.js - CultureWear Backend Server
const express = require('express');
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const JWT_SECRET = process.env.JWT_SECRET || 'culturewear_secret_key_change_in_production';
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/culturewear';

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public')); // Serve static HTML files from 'public' folder

// MongoDB Connection
const connectDB = async () => {
    try {
        await mongoose.connect(MONGODB_URI);
        console.log('✅ MongoDB connected successfully');
        console.log('📊 Database:', mongoose.connection.name);
    } catch (error) {
        console.error('❌ MongoDB connection error:', error.message);
        process.exit(1);
    }
};

// User Schema
const userSchema = new mongoose.Schema({
    // Basic Info (Step 1)
    firstName: {
        type: String,
        required: true,
        trim: true,
        maxlength: 50
    },
    lastName: {
        type: String,
        required: true,
        trim: true,
        maxlength: 50
    },
    email: {
        type: String,
        required: true,
        unique: true,
        lowercase: true,
        trim: true,
        match: [/^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/, 'Please enter a valid email']
    },
    password: {
        type: String,
        required: true,
        minlength: 6
    },
    
    // Profile & Preferences (Step 2)
    country: {
        type: String,
        required: true
    },
    timezone: {
        type: String,
        required: true
    },
    interests: [{
        type: String,
        enum: ['asian', 'european', 'african', 'latin', 'middle-eastern', 'indigenous']
    }],
    newsletter: {
        type: Boolean,
        default: false
    },
    
    // Wallet Setup (Step 3)
    walletType: {
        type: String,
        enum: ['xumm', 'metamask', 'ledger', 'skip'],
        default: 'skip'
    },
    walletAddress: {
        type: String,
        default: null
    },
    
    // Account Details
    stylePoints: {
        type: Number,
        default: 500 // Welcome bonus
    },
    isEmailVerified: {
        type: Boolean,
        default: false
    },
    loginMethod: {
        type: String,
        enum: ['email', 'google', 'apple', 'wallet'],
        default: 'email'
    },
    
    // Timestamps
    signupDate: {
        type: Date,
        default: Date.now
    },
    lastLogin: {
        type: Date,
        default: Date.now
    }
}, {
    timestamps: true // Adds createdAt and updatedAt automatically
});

// Password hashing middleware
userSchema.pre('save', async function(next) {
    // Only hash password if it's been modified (or is new)
    if (!this.isModified('password')) return next();
    
    try {
        // Hash password with cost of 12
        const saltRounds = 12;
        this.password = await bcrypt.hash(this.password, saltRounds);
        next();
    } catch (error) {
        next(error);
    }
});

// Instance method to check password
userSchema.methods.comparePassword = async function(candidatePassword) {
    return bcrypt.compare(candidatePassword, this.password);
};

// Instance method to generate JWT token
userSchema.methods.generateAuthToken = function() {
    return jwt.sign(
        { 
            id: this._id, 
            email: this.email,
            firstName: this.firstName
        }, 
        JWT_SECRET, 
        { expiresIn: '30d' }
    );
};

const User = mongoose.model('User', userSchema);

// Routes

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({ 
        status: 'healthy', 
        database: mongoose.connection.readyState === 1 ? 'connected' : 'disconnected',
        timestamp: new Date().toISOString()
    });
});

// User registration endpoint
app.post('/api/auth/signup', async (req, res) => {
    try {
        const {
            firstName,
            lastName,
            email,
            password,
            country,
            timezone,
            interests,
            newsletter,
            walletType,
            walletAddress
        } = req.body;

        // Check if user already exists
        const existingUser = await User.findOne({ email: email.toLowerCase() });
        if (existingUser) {
            return res.status(400).json({
                success: false,
                message: 'User with this email already exists'
            });
        }

        // Create new user
        const user = new User({
            firstName: firstName.trim(),
            lastName: lastName.trim(),
            email: email.toLowerCase().trim(),
            password,
            country,
            timezone,
            interests: interests || [],
            newsletter: newsletter || false,
            walletType: walletType || 'skip',
            walletAddress: walletAddress || null
        });

        // Save user to database (password will be hashed automatically)
        await user.save();

        // Generate auth token
        const token = user.generateAuthToken();

        // Remove password from response
        const userResponse = user.toObject();
        delete userResponse.password;

        console.log(`✅ New user registered: ${user.email}`);

        res.status(201).json({
            success: true,
            message: 'Account created successfully!',
            user: userResponse,
            token
        });

    } catch (error) {
        console.error('❌ Signup error:', error);
        
        if (error.code === 11000) {
            // Duplicate key error (email already exists)
            return res.status(400).json({
                success: false,
                message: 'User with this email already exists'
            });
        }
        
        if (error.name === 'ValidationError') {
            const errors = Object.values(error.errors).map(err => err.message);
            return res.status(400).json({
                success: false,
                message: 'Validation failed',
                errors
            });
        }

        res.status(500).json({
            success: false,
            message: 'Internal server error. Please try again.'
        });
    }
});

// User login endpoint
app.post('/api/auth/signin', async (req, res) => {
    try {
        const { email, password } = req.body;

        // Find user by email
        const user = await User.findOne({ email: email.toLowerCase() });
        if (!user) {
            return res.status(400).json({
                success: false,
                message: 'Invalid email or password'
            });
        }

        // Check password
        const isPasswordValid = await user.comparePassword(password);
        if (!isPasswordValid) {
            return res.status(400).json({
                success: false,
                message: 'Invalid email or password'
            });
        }

        // Update last login
        user.lastLogin = new Date();
        await user.save();

        // Generate auth token
        const token = user.generateAuthToken();

        // Remove password from response
        const userResponse = user.toObject();
        delete userResponse.password;

        console.log(`✅ User signed in: ${user.email}`);

        res.json({
            success: true,
            message: 'Login successful!',
            user: userResponse,
            token
        });

    } catch (error) {
        console.error('❌ Signin error:', error);
        res.status(500).json({
            success: false,
            message: 'Internal server error. Please try again.'
        });
    }
});

// Get user profile (protected route)
app.get('/api/user/profile', authenticateToken, async (req, res) => {
    try {
        const user = await User.findById(req.user.id).select('-password');
        if (!user) {
            return res.status(404).json({
                success: false,
                message: 'User not found'
            });
        }

        res.json({
            success: true,
            user
        });
    } catch (error) {
        console.error('❌ Profile fetch error:', error);
        res.status(500).json({
            success: false,
            message: 'Internal server error'
        });
    }
});

// Middleware to authenticate JWT tokens
function authenticateToken(req, res, next) {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

    if (!token) {
        return res.status(401).json({
            success: false,
            message: 'Access token required'
        });
    }

    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) {
            return res.status(403).json({
                success: false,
                message: 'Invalid or expired token'
            });
        }
        req.user = user;
        next();
    });
}

// Serve HTML files
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/signup', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'signup.html'));
});

app.get('/signin', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'signin.html'));
});

app.get('/dashboard', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'dashboard.html'));
});

// Start server
const startServer = async () => {
    await connectDB();
    app.listen(PORT, () => {
        console.log(`🚀 CultureWear server running on port ${PORT}`);
        console.log(`📱 Frontend: http://localhost:${PORT}`);
        console.log(`🔗 API: http://localhost:${PORT}/api`);
        console.log(`💾 Database: ${MONGODB_URI}`);
    });
};

startServer().catch(error => {
    console.error('❌ Server startup error:', error);
    process.exit(1);
});

module.exports = app;