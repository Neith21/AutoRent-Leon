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
    label: 'Tables',
    icon: mdiTable,
    menu: [
      {
        to: '/tables',
        label: 'Users',
        icon: mdiAccountCircle
      },
      {
        to: '/branches',
        label: 'Branches',
        icon: mdiAccountCircle
      }
    ]
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
