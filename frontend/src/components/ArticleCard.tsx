import React from 'react'
import { useQuery } from '@tanstack/react-query'
import dayjs from 'dayjs'
import api from '@/utils/api'

interface Article {
  id: number
  account_id: number
  title: string
  url: string
  author?: string
  published_at: string
  read_count: number
  like_count: number
  cover_image_url?: string
  created_at: string
}

interface ArticleCardProps {
  article: Article
}

export const ArticleCard: React.FC<ArticleCardProps> = ({ article }) => {
  const { data: summary } = useQuery({
    queryKey: ['summary', article.id],
    queryFn: async () => {
      const response = await api.get(`/articles/${article.id}/summary`)
      return response.data
    },
    enabled: false,
  })

  const [showSummary, setShowSummary] = React.useState(false)

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-4 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-3">
        <div className="flex-1">
          <h3 className="text-xl font-semibold text-gray-900 mb-2 line-clamp-2">
            <a href={article.url} target="_blank" rel="noopener noreferrer" className="hover:text-blue-600">
              {article.title}
            </a>
          </h3>
          <div className="text-sm text-gray-600">
            <span>{article.author && `作者: ${article.author}`}</span>
            {article.author && <span className="mx-2">•</span>}
            <span>{dayjs(article.published_at).format('YYYY-MM-DD HH:mm')}</span>
            <span className="mx-2">•</span>
            <span>阅读: {article.read_count}</span>
          </div>
        </div>
        {article.cover_image_url && (
          <img 
            src={article.cover_image_url} 
            alt={article.title}
            className="w-24 h-24 object-cover rounded ml-4"
          />
        )}
      </div>

      {showSummary && summary && (
        <div className="bg-blue-50 border-l-4 border-blue-500 p-4 my-4 rounded">
          <h4 className="font-semibold text-gray-900 mb-2">摘要</h4>
          <p className="text-gray-700 text-sm leading-relaxed">{summary.summary_text}</p>
        </div>
      )}

      <div className="flex gap-2 mt-4">
        <button
          onClick={() => setShowSummary(!showSummary)}
          className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
        >
          {showSummary ? '隐藏' : '显示'}摘要
        </button>
        <a 
          href={article.url}
          target="_blank" 
          rel="noopener noreferrer"
          className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
        >
          阅读原文
        </a>
      </div>
    </div>
  )
}
