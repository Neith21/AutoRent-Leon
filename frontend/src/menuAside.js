import {
  mdiAccountCircle,
  mdiMonitor,
  mdiSquareEditOutline,
  mdiTable,
} from '@mdi/js'

export default [
  {
    to: '/',
    icon: mdiMonitor,
    label: 'Dashboard',
  },
  {
    to: '/tables',
    label: 'Tables',
    icon: mdiTable,
  },
  {
    to: '/forms',
    label: 'Forms',
    icon: mdiSquareEditOutline,
  },
  {
    to: '/profile',
    label: 'Profile',
    icon: mdiAccountCircle,
  }
]
