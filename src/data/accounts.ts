import type { AccountRecord } from '@/types'

export const DEMO_PASSWORD = 'somnia123'

export const DEMO_ACCOUNTS: AccountRecord[] = [
  {
    email: 'guest@somnia.demo',
    password: DEMO_PASSWORD,
    role: 'guest',
    nickname: '林晚宁',
  },
  {
    email: 'manager@somnia.demo',
    password: DEMO_PASSWORD,
    role: 'manager',
    nickname: '值班经理',
  },
]
