import { mdiAccount, mdiLogout, mdiThemeLightDark } from '@mdi/js'

// No inicialices el store aquí
// let store = useAuthStore(); <- Eliminar esta línea

export default [
  {
    isCurrentUser: true,
    menu: [
      {
        icon: mdiAccount,
        label: 'My Profile',
        to: '/profile',
      }
    ],
  },
  {
    icon: mdiThemeLightDark,
    label: 'Light/Dark',
    isDesktopNoLabel: true,
    isToggleLightDark: true,
  }
]
