"use client";

import React, { useSyncExternalStore } from 'react';
import { usePathname } from 'next/navigation';

const subscribeToTheme = (onStoreChange: () => void) => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    mediaQuery.addEventListener('change', onStoreChange);
    return () => mediaQuery.removeEventListener('change', onStoreChange);
};

const getTheme = (): 'light' | 'dark' => (
    window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
);

interface LinkOption {
    label: string;
    href?: string;
}

interface NavbarProps {
    title: string;
    linkOptions?: LinkOption[];
    avatarUrl?: string;
    name: string;
    surname: string;
    lastname: string;
    variant?: 'default' | 'report';
}

const Navbar: React.FC<NavbarProps> = ({ title, linkOptions, avatarUrl, name, surname, lastname, variant = 'default' }) => {
    const theme = useSyncExternalStore(subscribeToTheme, getTheme, () => 'light');
    const pathname = usePathname();

    const logoSrc = theme === 'dark' ? '/csh/mpu_logo_d.png' : '/csh/mpu_logo_l.png';
    return (
        <aside className={`navbar-container ${variant === 'report' ? 'navbar-container--report' : ''}`}>
            <img className="theme-aware-logo" src={logoSrc} alt="Логотип Московского Политеха" width={250} height={66.21} style={{
                marginBottom: "14px",
            }} />
            <div className='line'></div>
            <div className='navbar-title-text-block'>
                <p>{title}</p>
            </div>
            <div className='navbar-avatar'>
                <img src={avatarUrl || "/csh/default_avatar.png"} alt="Avatar" width={100} height={100} />
            </div>
            <div className='navbar-text-container'>
                <p>{surname}</p>
                <p>{name} {lastname}</p>
            </div>
            <div className='navbar-link-container'>
                {linkOptions && linkOptions.map((option, index) => {
                    const pathnameWithoutBasePath = option.href?.replace(/^\/csh(?=\/|$)/, '');
                    const isActive = pathname === option.href || pathname === pathnameWithoutBasePath;

                    return (
                        <div key={index} className='navbar-inner-container'>
                            <div className={isActive ? 'navbar-active' : 'navbar-deactive'}></div>
                            {option.href ? (
                                <a
                                    href={option.href}
                                    className={isActive ? 'navbar-path navbar-active-path' : 'navbar-path navbar-deactive-path'}
                                    aria-current={isActive ? 'page' : undefined}
                                >
                                    {option.label}
                                </a>
                            ) : (
                                <span className="navbar-path navbar-deactive-path">{option.label}</span>
                            )}
                        </div>
                    );
                })}
            </div>
        </aside>
    );
}

export default Navbar;
