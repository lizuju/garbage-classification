// useAuthModal.js - Global Auth Modal State Management
import { ref } from 'vue'

// Modal types
export const MODAL_TYPES = {
    LOGIN: 'login',
    REGISTER: 'register',
    PROFILE: 'profile'
}

// Global state (shared across all components)
const isOpen = ref(false)
const modalType = ref(null)
const previousRoute = ref(null)

export function useAuthModal() {
    const openModal = (type, fromRoute = null) => {
        modalType.value = type
        previousRoute.value = fromRoute
        isOpen.value = true
        // Lock body scroll using CSS class
        document.body.classList.add('modal-open')
    }

    const closeModal = () => {
        isOpen.value = false
        modalType.value = null
        // Unlock body scroll
        document.body.classList.remove('modal-open')
    }

    const openLogin = (fromRoute = null) => openModal(MODAL_TYPES.LOGIN, fromRoute)
    const openRegister = (fromRoute = null) => openModal(MODAL_TYPES.REGISTER, fromRoute)
    const openProfile = (fromRoute = null) => openModal(MODAL_TYPES.PROFILE, fromRoute)

    // Switch between login and register within modal
    const switchToLogin = () => {
        modalType.value = MODAL_TYPES.LOGIN
    }

    const switchToRegister = () => {
        modalType.value = MODAL_TYPES.REGISTER
    }

    return {
        isOpen,
        modalType,
        previousRoute,
        openModal,
        closeModal,
        openLogin,
        openRegister,
        openProfile,
        switchToLogin,
        switchToRegister,
        MODAL_TYPES
    }
}
