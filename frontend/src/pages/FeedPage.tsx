import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '@/utils/api'
import { ArticleCard } from '@/components/ArticleCard'
import { AccountFilter } from '@/components/AccountFilter'
import { DatePicker } from '@/components/DatePicker'
import dayjs from 'dayjs'

export const FeedPage: React.FC = () => {
  const [selectedAccountId, setSelectedAccountId] = useState<number | undefined>()
  const [selectedDate, setSelectedDate] = useState(dayjs().format('YYYY-MM-DD'))

  const { data: articles, isLoading } = useQuery({
    queryKey: ['articles', selectedAccountId, selectedDate],
    queryFn: async () => {
      const params: any = {
        date: selectedDate,
        limit: 50
      }
      if (selectedAccountId) {
        params.account_id = selectedAccountId
      }
      const response = await api.get('/articles', { params })
      return response.data
    },
  })

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-6">文章流</h1>
        
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h3 className="font-semibold mb-4">筛选</h3>
          <AccountFilter selectedAccountId={selectedAccountId} onSelect={setSelectedAccountId} />
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">选择日期</label>
            <DatePicker value={selectedDate} onChange={setSelectedDate} />
          </div>
        </div>
      </div>

      {isLoading && (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="text-gray-600 mt-4">加载中...</p>
        </div>
      )}

      {!isLoading && (!articles || articles.length === 0) && (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-gray-600 text-lg">暂无文章</p>
        </div>
      )}

      {!isLoading && articles && articles.length > 0 && (
        <div>
          <p className="text-gray-600 mb-4">共 {articles.length} 篇文章</p>
          {articles.map((article: any) => (
            <ArticleCard key={article.id} article={article} />
          ))}
        </div>
      )}
    </div>
  )
}
