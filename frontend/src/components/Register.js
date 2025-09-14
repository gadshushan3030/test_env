import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { toast } from 'react-toastify';
import { authAPI } from '../api';
import './Auth.css';

const Register = ({ onRegister, onSwitchToLogin }) => {
  const [isLoading, setIsLoading] = useState(false);
  const { register, handleSubmit, formState: { errors }, watch } = useForm();

  const password = watch('password');

  const onSubmit = async (data) => {
    setIsLoading(true);
    try {
      // Call the API Gateway to create user
      const userData = {
        email: data.email,
        password: data.password,
        display_name: data.display_name,
        phone_number: data.phone_number
      };

      const response = await authAPI.register(userData);
      
      toast.success('הרשמה הושלמה בהצלחה!');
      onRegister(response);
    } catch (error) {
      toast.error('שגיאה בהרשמה: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>הרשמה</h2>
        <form onSubmit={handleSubmit(onSubmit)} className="auth-form">
          <div className="form-group">
            <label htmlFor="display_name">שם מלא:</label>
            <input
              type="text"
              id="display_name"
              {...register('display_name', { 
                required: 'שם מלא נדרש',
                minLength: {
                  value: 2,
                  message: 'שם חייב להכיל לפחות 2 תווים'
                }
              })}
              className={errors.display_name ? 'error' : ''}
            />
            {errors.display_name && <span className="error-message">{errors.display_name.message}</span>}
          </div>

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
            <label htmlFor="phone_number">טלפון (אופציונלי):</label>
            <input
              type="tel"
              id="phone_number"
              {...register('phone_number', {
                pattern: {
                  value: /^[0-9+\-\s()]+$/,
                  message: 'מספר טלפון לא תקין'
                }
              })}
              className={errors.phone_number ? 'error' : ''}
            />
            {errors.phone_number && <span className="error-message">{errors.phone_number.message}</span>}
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

          <div className="form-group">
            <label htmlFor="confirmPassword">אישור סיסמה:</label>
            <input
              type="password"
              id="confirmPassword"
              {...register('confirmPassword', { 
                required: 'אישור סיסמה נדרש',
                validate: value => value === password || 'סיסמאות לא תואמות'
              })}
              className={errors.confirmPassword ? 'error' : ''}
            />
            {errors.confirmPassword && <span className="error-message">{errors.confirmPassword.message}</span>}
          </div>

          <button 
            type="submit" 
            className="auth-button"
            disabled={isLoading}
          >
            {isLoading ? 'נרשם...' : 'הירשם'}
          </button>
        </form>

        <div className="auth-switch">
          <p>יש לך כבר חשבון? <button onClick={onSwitchToLogin} className="link-button">התחבר כאן</button></p>
        </div>
      </div>
    </div>
  );
};

export default Register;
