export interface TelegramWebApp {
  initData: string;
  initDataUnsafe: {
    query_id?: string;
    user?: {
      id: number;
      first_name: string;
      last_name?: string;
      username?: string;
      language_code?: string;
      is_premium?: boolean;
    };
    auth_date?: string;
    hash?: string;
  };
  version: string;
  platform: string;
  colorScheme: 'light' | 'dark';
  themeParams: Record<string, string>;
  isExpanded: boolean;
  viewportHeight: number;
  viewportStableHeight: number;
  headerColor: string;
  backgroundColor: string;
  BottomButton: any;
  MainButton: {
    text: string;
    color: string;
    textColor: string;
    isVisible: boolean;
    isActive: boolean;
    isProgressVisible: boolean;
    setText: (text: string) => void;
    onClick: (callback: () => void) => void;
    offClick: (callback: () => void) => void;
    show: () => void;
    hide: () => void;
    enable: () => void;
    disable: () => void;
    showProgress: (leaveActive: boolean) => void;
    hideProgress: () => void;
  };
  BackButton: {
    isVisible: boolean;
    onClick: (callback: () => void) => void;
    offClick: (callback: () => void) => void;
    show: () => void;
    hide: () => void;
  };
  HapticFeedback: {
    impactOccurred: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => void;
    notificationOccurred: (type: 'error' | 'success' | 'warning') => void;
    selectionChanged: () => void;
  };
  close: () => void;
  expand: () => void;
  ready: () => void;
  enableClosingConfirmation: () => void;
  disableClosingConfirmation: () => void;
  onEvent: (eventType: string, callback: () => void) => void;
  offEvent: (eventType: string, callback: () => void) => void;
  sendData: (data: string) => void;
  openLink: (url: string) => void;
  openTelegramLink: (url: string) => void;
  switchInlineQuery: (query: string, choose_chat_types?: string[]) => void;
}

declare global {
  interface Window {
    Telegram: {
      WebApp: TelegramWebApp;
    };
  }
}

export function getTelegramWebApp(): TelegramWebApp | null {
  try {
    if (window.Telegram?.WebApp) {
      return window.Telegram.WebApp;
    }
    return null;
  } catch {
    return null;
  }
}

export function getUserId(): string {
  const tg = getTelegramWebApp();
  if (tg?.initDataUnsafe?.user) {
    return String(tg.initDataUnsafe.user.id);
  }
  // Fallback for development
  const stored = localStorage.getItem('dev_user_id');
  if (stored) return stored;
  const devId = `dev_${Date.now()}`;
  localStorage.setItem('dev_user_id', devId);
  return devId;
}

export function getInitData(): string {
  const tg = getTelegramWebApp();
  if (tg?.initData) {
    return tg.initData;
  }
  return `query_id=dev&user=${encodeURIComponent(JSON.stringify({ id: getUserId(), first_name: 'Developer' }))}&auth_date=${Math.floor(Date.now() / 1000)}&hash=dev`;
}

export function getColorScheme(): 'light' | 'dark' {
  const tg = getTelegramWebApp();
  if (tg?.colorScheme) return tg.colorScheme;
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}
