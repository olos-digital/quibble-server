'use client'
import { forwardRef } from 'react';
import { FieldError } from 'react-hook-form';

interface Props extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string
  error?: FieldError
}

export const Input = forwardRef<HTMLInputElement, Props>(
  ({ label, error, ...rest }, ref) => (
    <div className="w-full">
      <label className="block mb-1 text-sm font-medium text-gray-700">
        {label}
      </label>
      <input
        ref={ref}
        className={`w-full rounded-md border px-3 py-2 text-sm shadow-sm
          focus:outline-none focus:ring-2 focus:ring-indigo-500 text-gray-500
          ${error ? 'border-rose-500' : 'border-gray-300'}`}
        {...rest}
      />
      {error && (
        <p className="mt-1 text-xs text-rose-600">{error.message}</p>
      )}
    </div>
  ),
)
Input.displayName = 'Input'
