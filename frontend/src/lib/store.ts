/**
 * Zustand store for Wela Meal Plan
 * Manages cart, checkout, and user preferences
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

// Types
export interface MenuItem {
  id: string
  name_en: string
  name_th?: string
  description_en: string
  base_price: number
  image_url?: string
  calories: number
  protein_g: number
  carbs_g: number
  fat_g: number
  is_gluten_free: boolean
  is_dairy_free: boolean
  is_halal: boolean
  spice_level: number
}

export interface CartItem {
  menuItem: MenuItem
  quantity: number
  modifiers: Modifier[]
  specialInstructions?: string
}

export interface Modifier {
  id: string
  name_en: string
  price_delta: number
}

export interface DeliveryAddress {
  label: string
  recipientName: string
  phone: string
  streetAddress: string
  unit?: string
  city: string
  province: string
  postalCode: string
  deliveryInstructions?: string
}

export interface DeliveryZone {
  id: string
  postal_code_prefix: string
  label: string
  delivery_fee: number
  free_delivery_threshold: number
}

export interface DeliveryWindow {
  id: string
  date: string
  time_start: string
  time_end: string
  display_time: string
  spots_remaining: number
}

// Store state
interface CartState {
  // Cart
  items: CartItem[]

  // Delivery
  deliveryAddress: DeliveryAddress | null
  deliveryZone: DeliveryZone | null
  deliveryWindow: DeliveryWindow | null

  // Discounts
  couponCode: string | null
  couponDiscount: number
  pointsToRedeem: number
  referralCode: string | null

  // Checkout step
  checkoutStep: 1 | 2

  // Actions
  addItem: (item: MenuItem, quantity?: number, modifiers?: Modifier[]) => void
  removeItem: (itemId: string) => void
  updateQuantity: (itemId: string, quantity: number) => void
  clearCart: () => void

  setDeliveryAddress: (address: DeliveryAddress) => void
  setDeliveryZone: (zone: DeliveryZone | null) => void
  setDeliveryWindow: (window: DeliveryWindow | null) => void

  setCoupon: (code: string | null, discount: number) => void
  setPointsToRedeem: (points: number) => void
  setReferralCode: (code: string | null) => void

  setCheckoutStep: (step: 1 | 2) => void

  // Computed
  getSubtotal: () => number
  getDeliveryFee: () => number
  getTaxAmount: () => number
  getTotal: () => number
  getTotalItems: () => number
  getTotalCalories: () => number
  getTotalProtein: () => number
}

const HST_RATE = 0.13

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      // Initial state
      items: [],
      deliveryAddress: null,
      deliveryZone: null,
      deliveryWindow: null,
      couponCode: null,
      couponDiscount: 0,
      pointsToRedeem: 0,
      referralCode: null,
      checkoutStep: 1,

      // Actions
      addItem: (item, quantity = 1, modifiers = []) => {
        set((state) => {
          const existingIndex = state.items.findIndex(
            (i) => i.menuItem.id === item.id
          )

          if (existingIndex >= 0) {
            const newItems = [...state.items]
            newItems[existingIndex].quantity += quantity
            return { items: newItems }
          }

          return {
            items: [...state.items, { menuItem: item, quantity, modifiers }]
          }
        })
      },

      removeItem: (itemId) => {
        set((state) => ({
          items: state.items.filter((i) => i.menuItem.id !== itemId)
        }))
      },

      updateQuantity: (itemId, quantity) => {
        set((state) => {
          if (quantity <= 0) {
            return { items: state.items.filter((i) => i.menuItem.id !== itemId) }
          }
          return {
            items: state.items.map((i) =>
              i.menuItem.id === itemId ? { ...i, quantity } : i
            )
          }
        })
      },

      clearCart: () => {
        set({
          items: [],
          couponCode: null,
          couponDiscount: 0,
          pointsToRedeem: 0,
        })
      },

      setDeliveryAddress: (address) => set({ deliveryAddress: address }),
      setDeliveryZone: (zone) => set({ deliveryZone: zone }),
      setDeliveryWindow: (window) => set({ deliveryWindow: window }),

      setCoupon: (code, discount) => set({ couponCode: code, couponDiscount: discount }),
      setPointsToRedeem: (points) => set({ pointsToRedeem: points }),
      setReferralCode: (code) => set({ referralCode: code }),

      setCheckoutStep: (step) => set({ checkoutStep: step }),

      // Computed values
      getSubtotal: () => {
        const { items } = get()
        return items.reduce((sum, item) => {
          const itemPrice = item.menuItem.base_price
          const modifiersPrice = item.modifiers.reduce((m, mod) => m + mod.price_delta, 0)
          return sum + (itemPrice + modifiersPrice) * item.quantity
        }, 0)
      },

      getDeliveryFee: () => {
        const { deliveryZone } = get()
        const subtotal = get().getSubtotal()

        if (!deliveryZone) return 0
        if (subtotal >= deliveryZone.free_delivery_threshold) return 0
        return deliveryZone.delivery_fee
      },

      getTaxAmount: () => {
        const subtotal = get().getSubtotal()
        const deliveryFee = get().getDeliveryFee()
        const { couponDiscount, pointsToRedeem } = get()
        const pointsValue = pointsToRedeem / 100 // 100 points = $1

        const taxableAmount = subtotal + deliveryFee - couponDiscount - pointsValue
        return Math.max(0, taxableAmount * HST_RATE)
      },

      getTotal: () => {
        const subtotal = get().getSubtotal()
        const deliveryFee = get().getDeliveryFee()
        const tax = get().getTaxAmount()
        const { couponDiscount, pointsToRedeem } = get()
        const pointsValue = pointsToRedeem / 100

        return Math.max(0, subtotal + deliveryFee + tax - couponDiscount - pointsValue)
      },

      getTotalItems: () => {
        return get().items.reduce((sum, item) => sum + item.quantity, 0)
      },

      getTotalCalories: () => {
        return get().items.reduce(
          (sum, item) => sum + item.menuItem.calories * item.quantity,
          0
        )
      },

      getTotalProtein: () => {
        return get().items.reduce(
          (sum, item) => sum + item.menuItem.protein_g * item.quantity,
          0
        )
      },
    }),
    {
      name: 'wela-cart',
      partialize: (state) => ({
        items: state.items,
        deliveryAddress: state.deliveryAddress,
        referralCode: state.referralCode,
      }),
    }
  )
)

// User preferences store
interface UserPreferences {
  language: 'en' | 'th'
  setLanguage: (lang: 'en' | 'th') => void
}

export const useUserPreferences = create<UserPreferences>()(
  persist(
    (set) => ({
      language: 'en',
      setLanguage: (lang) => set({ language: lang }),
    }),
    {
      name: 'wela-preferences',
    }
  )
)
