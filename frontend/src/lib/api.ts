/**
 * API client for Wela Meal Plan backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

interface ApiResponse<T> {
  status: 'success' | 'error'
  data: T | null
  message: string
}

// API Types
export interface MenuItem {
  id: string
  name_en: string
  name_th?: string
  description_en: string
  description_th?: string
  category: string
  base_price: string
  image_url?: string
  thumbnail_url?: string
  calories: number
  protein_g: number
  carbs_g: number
  fat_g: number
  fiber_g: number
  sodium_mg: number
  is_gluten_free: boolean
  is_dairy_free: boolean
  is_halal: boolean
  spice_level: number
  is_active: boolean
  is_featured: boolean
}

export interface DeliveryZone {
  id: string
  postal_code_prefix: string
  label: string
  city: string
  delivery_fee: string
  free_delivery_threshold: string
  is_active: boolean
}

export interface DeliveryWindow {
  id: string
  date: string
  start_time: string
  end_time: string
  spots_remaining: number
}

export interface CartItem {
  menu_item_id: string
  quantity: number
  modifiers?: string[]
}

export interface DeliveryAddress {
  name: string
  street_address: string
  city: string
  province: string
  postal_code: string
  phone: string
  delivery_instructions?: string
}

export interface LoyaltyTransaction {
  id: string
  points_delta: number
  balance_after: number
  reason: string
  reason_display: string
  description: string
  created_at: string
}

export interface UserProfile {
  user: {
    id: string
    email: string
    first_name: string
    last_name: string
    phone: string
    role: string
    created_at: string
  }
  wela_points_balance: number
  points_value: string
  referral_code: string
  preferred_language: 'en' | 'th'
  email_marketing_opt_in: boolean
  sms_opt_in: boolean
  dietary_notes: string
}

export interface SavedAddress {
  id: string
  label: string
  recipient_name: string
  phone: string
  street_address: string
  unit: string
  city: string
  province: string
  postal_code: string
  country: string
  delivery_instructions: string
  is_default: boolean
  full_address: string
}

export interface OrderItem {
  id: string
  menu_item: string
  menu_item_name: string
  quantity: number
  unit_price: string
  modifiers_snapshot: Record<string, unknown>
  modifiers_total: string
  special_instructions: string
  subtotal: string
}

export interface OrderData {
  id: string
  order_number: string
  status: string
  status_display: string
  subtotal: string
  discount_amount: string
  delivery_fee: string
  tax_rate: string
  tax_amount: string
  tax_type: string
  total: string
  points_earned: number
  points_redeemed: number
  points_redemption_value: string
  delivery_date: string | null
  delivery_window_display: string | null
  customer_notes: string
  delivery_address_snapshot: Record<string, unknown>
  created_at: string
  confirmed_at: string | null
  delivered_at: string | null
  items: OrderItem[]
}

export interface SubscriptionItem {
  id: string
  menu_item: string
  menu_item_name: string
  quantity: number
  week_number: number
  modifiers: Record<string, unknown>
}

export interface SubscriptionData {
  id: string
  plan_type: string
  plan_type_display: string
  billing_cycle: string
  status: string
  status_display: string
  next_billing_date: string | null
  last_billing_date: string | null
  price_per_cycle: string
  free_delivery: boolean
  discount_percentage: string
  pause_until_date: string | null
  skipped_weeks: string[]
  created_at: string
  items: SubscriptionItem[]
}

export interface ReferralInfo {
  referral_code: string
  referral_url: string
  total_referrals: number
  pending_rewards: number
  earned_points: number
}

class ApiClient {
  private baseUrl: string
  private token: string | null = null

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  setToken(token: string | null) {
    this.token = token
  }

  getToken() {
    return this.token
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...((options.headers as Record<string, string>) || {}),
    }

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`
    }

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        headers,
      })

      const data = await response.json()

      if (!response.ok) {
        return {
          status: 'error',
          data: null,
          message: data.message || data.detail || `HTTP error ${response.status}`,
        }
      }

      return data as ApiResponse<T>
    } catch (error) {
      return {
        status: 'error',
        data: null,
        message: error instanceof Error ? error.message : 'Network error',
      }
    }
  }

  // Menu endpoints
  async getMenuItems(params?: Record<string, string>) {
    const query = params ? '?' + new URLSearchParams(params).toString() : ''
    return this.request<MenuItem[]>(`/menu/${query}`)
  }

  async getMenuItem(id: string) {
    return this.request<MenuItem>(`/menu/${id}/`)
  }

  // Delivery endpoints
  async getDeliveryZones() {
    return this.request<DeliveryZone[]>('/delivery/zones/')
  }

  async validatePostalCode(postalCode: string) {
    return this.request<{
      serviceable: boolean
      zone: DeliveryZone | null
      delivery_fee: string
      free_delivery_threshold: string
      next_delivery_window: DeliveryWindow | null
    }>('/delivery/validate-postal/', {
      method: 'POST',
      body: JSON.stringify({ postal_code: postalCode }),
    })
  }

  // Checkout endpoints
  async createPaymentIntent(data: {
    items: CartItem[]
    delivery_address: DeliveryAddress
    delivery_window_id: string
    coupon_code?: string
    points_to_redeem?: number
  }) {
    return this.request<{ client_secret: string }>('/checkout/create-intent/', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async confirmOrder(paymentIntentId: string) {
    return this.request<{ order_number: string }>('/checkout/confirm/', {
      method: 'POST',
      body: JSON.stringify({ payment_intent_id: paymentIntentId }),
    })
  }

  // Coupon endpoints
  async validateCoupon(code: string, subtotal: number) {
    return this.request<{
      valid: boolean
      discount_amount: string
      discount_type: string
    }>('/coupons/validate/', {
      method: 'POST',
      body: JSON.stringify({ code, subtotal }),
    })
  }

  // Auth endpoints
  async login(email: string, password: string) {
    return this.request<{ access: string; refresh: string }>('/auth/token/', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
  }

  async refreshToken(refreshToken: string) {
    return this.request<{ access: string }>('/auth/token/refresh/', {
      method: 'POST',
      body: JSON.stringify({ refresh: refreshToken }),
    })
  }

  async register(data: { email: string; password: string; first_name: string; last_name: string; phone?: string }) {
    return this.request<{ id: string; email: string }>('/auth/register/', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  // Profile endpoints
  async getProfile() {
    return this.request<UserProfile>('/auth/profile/')
  }

  async updateProfile(data: Partial<{ preferred_language: string; email_marketing_opt_in: boolean; sms_opt_in: boolean; dietary_notes: string }>) {
    return this.request<UserProfile>('/auth/profile/', {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  // Address endpoints
  async getAddresses() {
    return this.request<SavedAddress[]>('/auth/addresses/')
  }

  async createAddress(data: Partial<SavedAddress>) {
    return this.request<SavedAddress>('/auth/addresses/', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async updateAddress(id: string, data: Partial<SavedAddress>) {
    return this.request<SavedAddress>(`/auth/addresses/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  async deleteAddress(id: string) {
    return this.request<null>(`/auth/addresses/${id}/`, {
      method: 'DELETE',
    })
  }

  async setDefaultAddress(id: string) {
    return this.request<SavedAddress>(`/auth/addresses/${id}/set-default/`, {
      method: 'POST',
    })
  }

  // Order endpoints
  async getOrders() {
    return this.request<OrderData[]>('/checkout/my/')
  }

  // Subscription endpoints
  async getSubscription() {
    return this.request<SubscriptionData | null>('/subscriptions/current/')
  }

  async pauseSubscription(pauseUntilDate: string) {
    return this.request<null>('/subscriptions/pause/', {
      method: 'POST',
      body: JSON.stringify({ pause_until_date: pauseUntilDate }),
    })
  }

  async resumeSubscription() {
    return this.request<null>('/subscriptions/resume/', { method: 'POST' })
  }

  async cancelSubscription(reason?: string) {
    return this.request<null>('/subscriptions/cancel/', {
      method: 'POST',
      body: JSON.stringify({ reason }),
    })
  }

  async skipWeek(weekDate: string) {
    return this.request<null>('/subscriptions/skip-week/', {
      method: 'POST',
      body: JSON.stringify({ week_date: weekDate }),
    })
  }

  // Loyalty endpoints
  async getLoyaltyBalance() {
    return this.request<{
      balance: number
      dollar_value: string
      recent_transactions: LoyaltyTransaction[]
    }>('/loyalty/balance/')
  }

  async redeemPoints(points: number) {
    return this.request<{
      points_redeemed: number
      discount_applied: string
      remaining_balance: number
    }>('/loyalty/redeem/', {
      method: 'POST',
      body: JSON.stringify({ points }),
    })
  }

  // Referral endpoints
  async getReferralLink() {
    return this.request<ReferralInfo>('/referral/link/')
  }

  async applyReferralCode(code: string) {
    return this.request<{ discount_percent: number }>('/referral/apply/', {
      method: 'POST',
      body: JSON.stringify({ code }),
    })
  }
}

export const api = new ApiClient(API_BASE_URL)
