import {
  mdiAccountCircle,
  mdiMonitor,
  mdiSquareEditOutline,
  mdiTable,
  mdiCarBack,
  mdiDomain,
  mdiSourceBranch,
  mdiAccountGroup,
  mdiAccountGroupOutline,
  mdiCarInfo,
  mdiAccountMultiple
} from '@mdi/js'

export default [
  {
    to: '/',
    icon: mdiMonitor,
    label: 'Panel',
  },
  {
    label: 'Usuarios',
    icon: mdiAccountGroup,
    menu: [
      {
        to: '/tables',
        label: 'Usuarios',
        icon: mdiAccountGroupOutline, 
        requiredPermission: 'user.view_user'
      }
    ]
  },
  {
    label: 'Clientes',
    icon: mdiAccountMultiple,
    menu: [
      {
        to: '/customers',
        label: 'Clientes',
        icon: mdiAccountMultiple,
        requiredPermission: 'customer.view_customer'
      }
    ]
  },
  {
    label: 'Administración',
    icon: mdiDomain,
    menu: [
      {
        to: '/branches',
        label: 'Sucursales',
        icon: mdiSourceBranch,
        requiredPermission: 'branch.view_branch'
      }
    ]
  },
  {
    label: 'Vehículos',
    icon: mdiCarBack,
    menu: [
      {
        to: '/vehiclemodels',
        label: 'Modelos',
        icon: mdiCarInfo,
        requiredPermission: 'vehiclemodel.view_vehiclemodel'
      },
      {
        to: '/vehicles',
        label: 'Vehículos',
        icon: mdiCarBack,
        requiredPermission: 'vehicle.view_vehicle'
      }
    ]
  },
  {
    to: '/profile',
    label: 'Pefil',
    icon: mdiAccountCircle,
  }
]
