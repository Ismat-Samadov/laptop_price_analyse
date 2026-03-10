'use client';

import { motion } from 'framer-motion';
import clsx from 'clsx';
import { ButtonHTMLAttributes, ReactNode } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  children: ReactNode;
}

const VARIANT_CLASSES = {
  primary:
    'bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white shadow-[0_0_20px_rgba(124,58,237,0.4)]',
  secondary:
    'bg-white/10 hover:bg-white/20 border border-white/20 text-white',
  danger:
    'bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white',
  ghost:
    'bg-transparent hover:bg-white/10 text-white/70 hover:text-white',
};

const SIZE_CLASSES = {
  sm: 'px-3 py-1.5 text-sm rounded-lg',
  md: 'px-5 py-2.5 text-base rounded-xl',
  lg: 'px-8 py-3.5 text-lg rounded-xl',
};

export default function Button({
  variant = 'primary',
  size = 'md',
  className,
  children,
  disabled,
  ...props
}: ButtonProps) {
  return (
    <motion.button
      whileHover={!disabled ? { scale: 1.04 } : undefined}
      whileTap={!disabled ? { scale: 0.96 } : undefined}
      {...(props as any)}
      disabled={disabled}
      className={clsx(
        'font-semibold transition-all duration-150 outline-none focus-visible:ring-2 focus-visible:ring-white/50',
        VARIANT_CLASSES[variant],
        SIZE_CLASSES[size],
        disabled && 'opacity-40 cursor-not-allowed',
        className,
      )}
    >
      {children}
    </motion.button>
  );
}
