"use client";

import React, { useState } from 'react';

interface AlertProps {
  type: string;
  title: string;
  text: string;
}

const getLogo = (type: string) => {
    switch (type) {
        case 'success':
            return (
                <svg width="26" height="18" viewBox="0 0 26 18" fill="none" xmlns="http://www.w3.org/2000/svg" style={{
                    marginLeft: '7px',
                    marginTop: '11px',
                }}>
                    <path d="M9.02501 16.7098C8.63149 16.3228 8.63149 15.6953 9.02501 15.3084L23.2798 1.29024C23.6733 0.903254 24.3113 0.903253 24.7049 1.29024C25.0984 1.67722 25.0984 2.30465 24.7049 2.69163L10.4501 16.7098C10.0565 17.0967 9.41852 17.0967 9.02501 16.7098Z" stroke="var(--background-main-element-c)" strokeWidth="2"/>
                    <path d="M1.29514 7.72456C1.68866 7.33757 2.32668 7.33757 2.7202 7.72456L10.4316 15.3079C10.8251 15.6949 10.8251 16.3223 10.4316 16.7093C10.0381 17.0963 9.40006 17.0963 9.00654 16.7093L1.29514 9.12595C0.90162 8.73897 0.901621 8.11154 1.29514 7.72456Z" stroke="var(--background-main-element-c)" strokeWidth="2"/>
                </svg>
            );
        case 'error':
            return (
                <svg width="23" height="23" viewBox="0 0 23 23" fill="none" xmlns="http://www.w3.org/2000/svg" style={{
                    marginLeft: '9px',
                    marginTop: '9px',
                    height: '21px',
                    width: '21px',
                }}>
                    <path d="M1.30173 21.6983C0.899422 21.296 0.899422 20.6437 1.30173 20.2414L20.2414 1.30173C20.6437 0.899422 21.296 0.899423 21.6983 1.30173C22.1006 1.70404 22.1006 2.35632 21.6983 2.75863L2.75863 21.6983C2.35632 22.1006 1.70404 22.1006 1.30173 21.6983Z" stroke="var(--background-main-element-c)" strokeWidth="2"/>
                    <path d="M1.30173 1.30173C1.70404 0.899423 2.35632 0.899423 2.75863 1.30173L21.6983 20.2414C22.1006 20.6437 22.1006 21.296 21.6983 21.6983C21.296 22.1006 20.6437 22.1006 20.2414 21.6983L1.30173 2.75863C0.899422 2.35632 0.899423 1.70404 1.30173 1.30173Z" stroke="var(--background-main-element-c)" strokeWidth="2"/>
                </svg>

            );
        case 'warning':
            return (
                <svg width="31" height="28" viewBox="0 0 31 28" fill="none" xmlns="http://www.w3.org/2000/svg" style={{
                    marginLeft: '4px',
                    marginTop: '4px',
                    height: '30px',
                    width: '30px',
                }}>
                    <path d="M13.1938 2.59863C14.1779 1.13403 16.3504 1.13404 17.3345 2.59863L17.4292 2.75L28.688 22.25C29.65 23.9165 28.4471 25.9997 26.5229 26H4.00537C2.08121 25.9997 0.878358 23.9165 1.84033 22.25L13.0991 2.75L13.1938 2.59863Z" stroke="var(--background-main-element-c)" strokeWidth="3"/>
                    <rect x="14.7642" y="9.56445" width="1" height="7" rx="0.5" stroke="var(--background-main-element-c)" strokeWidth="2.5"/>
                    <circle cx="15.2642" cy="21.3013" r="2" fill="var(--background-main-element-c)"/>
                </svg>

            );
        case 'info':
            return (
                <svg width="4" height="21" viewBox="0 0 4 21" fill="none" xmlns="http://www.w3.org/2000/svg" style={{
                    marginLeft: '17px',
                    marginTop: '9.18px',
                }}>
                    <path d="M1.50049 8.28088C1.50049 8.00474 1.72435 7.78088 2.00049 7.78088C2.27663 7.78088 2.50049 8.00474 2.50049 8.28088V18.2809C2.50049 18.557 2.27663 18.7809 2.00049 18.7809C1.72435 18.7809 1.50049 18.557 1.50049 18.2809V8.28088Z" fill="var(--background-main-element-c)" stroke="var(--background-main-element-c)" strokeWidth="2.5"/>
                    <circle cx="2" cy="2" r="2" fill="var(--background-main-element-c)"/>
                </svg>

            );
        default:
            return '';
    }
};

const Alert: React.FC<AlertProps> = ({
    type,
    title,
    text
 }) => {
    const [isVisible, setIsVisible] = useState(true);

    const handleClose = () => {
        setIsVisible(false);
    };

    if (!isVisible) {
        return null;
    }
    return (
        <div className='alert-container'>
            <div className={`alert-icon  alert-icon-${type}`}>
                {getLogo(type)}
            </div>
            <div className='alert-text-conteiner'>
                <p className="text text-bold alert-text">{title}</p>
                <p className="text text-blind alert-text">{text}</p>
            </div>
            <button className='alert-close' onClick={handleClose}>
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg" style={{
                    pointerEvents: 'none',
                    marginLeft: '0px',
                    marginTop: '0px',
                }}>
                    <path d="M6.29297 7.97168L0.819336 13.4453C0.746391 13.5183 0.627632 13.5183 0.554688 13.4453C0.481742 13.3724 0.481742 13.2536 0.554688 13.1807L6.02832 7.70703L6.29297 7.97168ZM13.4453 13.1807C13.5183 13.2536 13.5183 13.3724 13.4453 13.4453C13.3724 13.5183 13.2536 13.5183 13.1807 13.4453L7.70703 7.97168L7.97168 7.70703L13.4453 13.1807ZM7.26465 7L7 7.26465L6.73535 7L7 6.73535L7.26465 7ZM0.554688 0.554688C0.627632 0.481743 0.746391 0.481743 0.819336 0.554688L6.29297 6.02832L6.02832 6.29297L0.554688 0.819336C0.481743 0.746391 0.481742 0.627633 0.554688 0.554688ZM13.1807 0.554688C13.2536 0.481742 13.3724 0.481742 13.4453 0.554688C13.5183 0.627632 13.5183 0.746391 13.4453 0.819336L7.97168 6.29297L7.70703 6.02832L13.1807 0.554688Z" stroke="var(--secondary-font-c)"/>
                </svg>

            </button>
        </div>
    );
}

export default Alert;