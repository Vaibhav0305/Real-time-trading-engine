import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './Auth.css';

const Login = () => {
  const navigate = useNavigate();
  const { login, isAuthenticated } = useAuth();
  
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  
  const [otpData, setOtpData] = useState({
    otp_code: '',
    user_id: '',
    otp_type: ''
  });
  
  const [currentStep, setCurrentStep] = useState('login'); // login, otp, 2fa
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    if (currentStep === 'login') {
      setFormData(prev => ({ ...prev, [name]: value }));
    } else {
      setOtpData(prev => ({ ...prev, [name]: value }));
    }
    setError('');
  };
  
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      const data = await response.json();
      
      if (data.success) {
        if (data.requires_2fa) {
          setOtpData(prev => ({ 
            ...prev, 
            user_id: data.user_id, 
            otp_type: '2fa' 
          }));
          setCurrentStep('2fa');
          setSuccess('2FA OTP sent to your phone');
        } else {
          // Store tokens
          localStorage.setItem('access_token', data.access_token);
          localStorage.setItem('refresh_token', data.refresh_token);
          if (rememberMe) {
            localStorage.setItem('username', formData.username);
          }
          
          // Login to context
          await login(data.access_token);
          setSuccess('Login successful! Redirecting...');
          
          setTimeout(() => {
            navigate('/dashboard');
          }, 1000);
        }
      } else {
        setError(data.error || 'Login failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  const handleOtpVerification = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('/api/v1/auth/verify-otp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(otpData),
      });
      
      const data = await response.json();
      
      if (data.success) {
        if (otpData.otp_type === 'verification') {
          setSuccess('Account verified! Please login.');
          setCurrentStep('login');
        } else if (otpData.otp_type === '2fa') {
          // Complete 2FA login
          setSuccess('2FA verified! Completing login...');
          // You would need to complete the login process here
          // This might require another API call
        }
      } else {
        setError(data.error || 'OTP verification failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  const handleResendOtp = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`/api/v1/auth/resend-otp?user_id=${otpData.user_id}&otp_type=${otpData.otp_type}`, {
        method: 'POST',
      });
      
      const data = await response.json();
      
      if (data.success) {
        setSuccess('OTP resent successfully!');
      } else {
        setError(data.error || 'Failed to resend OTP');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  const handleForgotPassword = () => {
    navigate('/forgot-password');
  };
  
  const handleRegister = () => {
    navigate('/register');
  };
  
  const renderLoginForm = () => (
    <div className="auth-form-container">
      <div className="auth-header">
        <h1>Welcome Back</h1>
        <p>Sign in to your VittCott account</p>
      </div>
      
      <form onSubmit={handleLogin} className="auth-form">
        <div className="form-group">
          <label htmlFor="username">Username</label>
          <div className="input-wrapper">
            <i className="fas fa-user"></i>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleInputChange}
              placeholder="Enter your username"
              required
            />
          </div>
        </div>
        
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <div className="input-wrapper">
            <i className="fas fa-lock"></i>
            <input
              type={showPassword ? 'text' : 'password'}
              id="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              placeholder="Enter your password"
              required
            />
            <button
              type="button"
              className="password-toggle"
              onClick={() => setShowPassword(!showPassword)}
            >
              <i className={`fas fa-${showPassword ? 'eye-slash' : 'eye'}`}></i>
            </button>
          </div>
        </div>
        
        <div className="form-options">
          <label className="checkbox-wrapper">
            <input
              type="checkbox"
              checked={rememberMe}
              onChange={(e) => setRememberMe(e.target.checked)}
            />
            <span className="checkmark"></span>
            Remember me
          </label>
          
          <button
            type="button"
            className="forgot-password-link"
            onClick={handleForgotPassword}
          >
            Forgot Password?
          </button>
        </div>
        
        <button
          type="submit"
          className="auth-button primary"
          disabled={loading}
        >
          {loading ? (
            <span className="loading-spinner">
              <i className="fas fa-spinner fa-spin"></i>
              Signing In...
            </span>
          ) : (
            'Sign In'
          )}
        </button>
      </form>
      
      <div className="auth-footer">
        <p>
          Don't have an account?{' '}
          <button
            type="button"
            className="link-button"
            onClick={handleRegister}
          >
            Sign Up
          </button>
        </p>
      </div>
    </div>
  );
  
  const renderOtpForm = () => (
    <div className="auth-form-container">
      <div className="auth-header">
        <h1>Verify OTP</h1>
        <p>Enter the verification code sent to your phone</p>
      </div>
      
      <form onSubmit={handleOtpVerification} className="auth-form">
        <div className="form-group">
          <label htmlFor="otp_code">Verification Code</label>
          <div className="input-wrapper otp-input">
            <i className="fas fa-key"></i>
            <input
              type="text"
              id="otp_code"
              name="otp_code"
              value={otpData.otp_code}
              onChange={handleInputChange}
              placeholder="Enter 6-digit code"
              maxLength="6"
              pattern="[0-9]{6}"
              required
            />
          </div>
          <small className="otp-hint">
            Enter the 6-digit code sent to your phone
          </small>
        </div>
        
        <button
          type="submit"
          className="auth-button primary"
          disabled={loading}
        >
          {loading ? (
            <span className="loading-spinner">
              <i className="fas fa-spinner fa-spin"></i>
              Verifying...
            </span>
          ) : (
            'Verify OTP'
          )}
        </button>
        
        <div className="otp-actions">
          <button
            type="button"
            className="auth-button secondary"
            onClick={handleResendOtp}
            disabled={loading}
          >
            Resend OTP
          </button>
          
          <button
            type="button"
            className="auth-button secondary"
            onClick={() => setCurrentStep('login')}
          >
            Back to Login
          </button>
        </div>
      </form>
    </div>
  );
  
  return (
    <div className="auth-page">
      <div className="auth-background">
        <div className="auth-background-overlay"></div>
        <div className="auth-background-content">
          <h2>VittCott Trading Platform</h2>
          <p>Advanced algorithmic trading with AI-powered insights</p>
        </div>
      </div>
      
      <div className="auth-content">
        {currentStep === 'login' ? renderLoginForm() : renderOtpForm()}
        
        {error && (
          <div className="alert alert-error">
            <i className="fas fa-exclamation-circle"></i>
            {error}
          </div>
        )}
        
        {success && (
          <div className="alert alert-success">
            <i className="fas fa-check-circle"></i>
            {success}
          </div>
        )}
      </div>
    </div>
  );
};

export default Login;
