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
        icon: mdiAccountCircle,
        requiredPermission: 'user.view_user'
      },
      {
        to: '/branches',
        label: 'Branches',
        icon: mdiAccountCircle,
        requiredPermission: 'branch.view_branch'
      },
      {
        to: '/vehicles',
        label: 'Vehicles',
        icon: mdiAccountCircle,
        requiredPermission: 'vehicle.view_vehicle'
      }
    ]
  },
  {
    to: '/profile',
    label: 'Profile',
    icon: mdiAccountCircle,
  }
]
