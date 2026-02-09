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
let savedScrollY = 0
let lastKnownScrollY = 0

const getScrollY = () => window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0

if (typeof window !== 'undefined') {
    window.addEventListener('scroll', () => {
        if (!isOpen.value) {
            lastKnownScrollY = getScrollY()
        }
    }, { passive: true })

    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') {
            const targetY = isOpen.value ? savedScrollY : lastKnownScrollY
            requestAnimationFrame(() => {
                window.scrollTo(0, targetY)
            })
        }
    })
}

export function useAuthModal() {
    const openModal = (type, fromRoute = null) => {
        modalType.value = type
        previousRoute.value = fromRoute
        isOpen.value = true
        // Lock body scroll using CSS class
        savedScrollY = getScrollY()
        document.body.classList.add('modal-open')
        document.body.style.top = `-${savedScrollY}px`
        document.body.style.position = 'fixed'
        document.body.style.width = '100%'
    }

    const closeModal = () => {
        isOpen.value = false
        modalType.value = null
        // Unlock body scroll
        const html = document.documentElement
        const prevScrollBehavior = html.style.scrollBehavior
        html.style.scrollBehavior = 'auto'
        document.body.classList.remove('modal-open')
        const offsetY = savedScrollY
        document.body.style.top = ''
        document.body.style.position = ''
        document.body.style.width = ''
        window.scrollTo(0, offsetY)
        requestAnimationFrame(() => {
            html.style.scrollBehavior = prevScrollBehavior
        })
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
