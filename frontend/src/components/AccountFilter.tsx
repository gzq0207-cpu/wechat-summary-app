import React from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '@/utils/api'

interface AccountFilterProps {
  selectedAccountId?: number
  onSelect: (accountId?: number) => void
}

export const AccountFilter: React.FC<AccountFilterProps> = ({ selectedAccountId, onSelect }) => {
  const { data: accounts } = useQuery({
    queryKey: ['accounts'],
    queryFn: async () => {
      const response = await api.get('/accounts')
      return response.data
    },
  })

  return (
    <div className="flex gap-2 mb-6 flex-wrap">
      <button
        onClick={() => onSelect(undefined)}
        className={`px-4 py-2 rounded-md font-medium transition-colors ${
          selectedAccountId === undefined
            ? 'bg-blue-600 text-white'
            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
        }`}
      >
        全部公众号
      </button>
      {accounts?.map((account: any) => (
        <button
          key={account.id}
          onClick={() => onSelect(account.id)}
          className={`px-4 py-2 rounded-md font-medium transition-colors ${
            selectedAccountId === account.id
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          {account.name}
        </button>
      ))}
    </div>
  )
}
