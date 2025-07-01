import { useState } from 'react'

export const useToast = () => {
  const [toasts, setToasts] = useState([])

  const toast = ({ title, description, variant = 'default' }) => {
    const id = Date.now()
    const newToast = { id, title, description, variant }
    
    setToasts(prev => [...prev, newToast])
    
    // Auto-remove toast after 5 seconds
    setTimeout(() => {
      setToasts(prev => prev.filter(toast => toast.id !== id))
    }, 5000)
    
    // For now, we'll just console.log the toast
    console.log(`Toast: ${title} - ${description}`)
  }

  const dismiss = (id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id))
  }

  return { toast, toasts, dismiss }
}

