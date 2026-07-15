export interface NavItem {
  label: string;
  to: string;
}

export interface NavGroup {
  label: string;
  items: NavItem[];
}

export const sidebarNavGroups: NavGroup[] = [
  {
    label: 'OPERATIONS',
    items: [{ label: 'Run Operation', to: '/operations' }],
  },
  {
    label: 'FEATURES',
    items: [
      { label: 'Service Health', to: '/health' },
      { label: 'Compare Performance', to: '/compare' },
      { label: 'Recent History', to: '/history' },
    ],
  },
  {
    label: 'MIGRATION',
    items: [{ label: 'Start Migration', to: '/migration' }],
  },
  {
    label: 'LEARN',
    items: [{ label: 'What Are Microservices?', to: '/learn' }],
  },
];
