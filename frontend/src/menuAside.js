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
  mdiAccountMultiple,
  mdiCarSports,
  mdiShapePlusOutline,
  mdiInvoiceEditOutline,
  mdiDomainPlus
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
        to: '/company-profile',
        label: 'Perfil de Empresa',
        icon: mdiDomainPlus,
        requiredPermission: 'company.view_company'
      },
      {
        to: '/branches',
        label: 'Sucursales',
        icon: mdiSourceBranch,
        requiredPermission: 'branch.view_branch'
      },
      {
        to: '/rentals',
        label: 'Alquileres',
        icon: mdiSquareEditOutline,
        requiredPermission: 'rental.view_rental'
      },
      {
        to: '/invoices/create',
        label: 'Facturas',
        icon: mdiInvoiceEditOutline,
        requiredPermission: 'invoice.view_invoice'
      }
    ]
  },
  {
    label: 'Vehículos',
    icon: mdiCarBack,
    menu: [
      {
        to: '/vehiclecategories',
        label: 'Categorías',
        icon: mdiShapePlusOutline,
        requiredPermission: 'vehiclecategory.view_vehiclecategory'
      },
      {
        to: '/brands',
        label: 'Marcas',
        icon: mdiCarSports,
        requiredPermission: 'brand.view_brand'
      },
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
