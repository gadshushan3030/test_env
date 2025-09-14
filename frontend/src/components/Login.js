import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { toast } from 'react-toastify';
import './Auth.css';

const Login = ({ onLogin, onSwitchToRegister }) => {
  const [isLoading, setIsLoading] = useState(false);
  const { register, handleSubmit, formState: { errors } } = useForm();

  const onSubmit = async (data) => {
    setIsLoading(true);
    try {
      // For demo purposes, we'll simulate a login
      // In a real app, you'd call your authentication API
      const mockUser = {
        id: '1',
        email: data.email,
        display_name: 'Demo User'
      };
      
      localStorage.setItem('authToken', 'demo-token');
      localStorage.setItem('user', JSON.stringify(mockUser));
      
      toast.success('התחברת בהצלחה!');
      onLogin(mockUser);
    } catch (error) {
      toast.error('שגיאה בהתחברות: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>התחברות</h2>
        <form onSubmit={handleSubmit(onSubmit)} className="auth-form">
          <div className="form-group">
            <label htmlFor="email">אימייל:</label>
            <input
              type="email"
              id="email"
              {...register('email', { 
                required: 'אימייל נדרש',
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: 'אימייל לא תקין'
                }
              })}
              className={errors.email ? 'error' : ''}
            />
            {errors.email && <span className="error-message">{errors.email.message}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="password">סיסמה:</label>
            <input
              type="password"
              id="password"
              {...register('password', { 
                required: 'סיסמה נדרשת',
                minLength: {
                  value: 6,
                  message: 'סיסמה חייבת להכיל לפחות 6 תווים'
                }
              })}
              className={errors.password ? 'error' : ''}
            />
            {errors.password && <span className="error-message">{errors.password.message}</span>}
          </div>

          <button 
            type="submit" 
            className="auth-button"
            disabled={isLoading}
          >
            {isLoading ? 'מתחבר...' : 'התחבר'}
          </button>
        </form>

        <div className="auth-switch">
          <p>אין לך חשבון? <button onClick={onSwitchToRegister} className="link-button">הירשם כאן</button></p>
        </div>
      </div>
    </div>
  );
};

export default Login;
