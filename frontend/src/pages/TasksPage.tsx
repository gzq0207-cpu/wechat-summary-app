import React from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import api from '@/utils/api'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

export const TasksPage: React.FC = () => {
  const { data: status, isLoading, refetch } = useQuery({
    queryKey: ['taskStatus'],
    queryFn: async () => {
      const response = await api.get('/tasks/status')
      return response.data
    },
    refetchInterval: 5000, // 每5秒刷新一次
  })

  const { data: logs } = useQuery({
    queryKey: ['crawlLogs'],
    queryFn: async () => {
      const response = await api.get('/tasks/logs')
      return response.data
    },
    refetchInterval: 10000, // 每10秒刷新一次
  })

  const runJobMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post('/tasks/run-now')
      return response.data
    },
    onSuccess: () => {
      refetch()
    }
  })

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">爬虫任务管理</h1>

      <div className="grid md:grid-cols-2 gap-6 mb-8">
        {/* 任务状态卡片 */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">任务状态</h2>
          {isLoading ? (
            <p className="text-gray-600">加载中...</p>
          ) : status ? (
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-600">运行状态</p>
                <p className="text-lg font-semibold">{status.is_running ? '🔄 运行中' : '✅ 就绪'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">公众号总数</p>
                <p className="text-lg font-semibold">{status.total_accounts}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">已启用公众号</p>
                <p className="text-lg font-semibold text-blue-600">{status.active_accounts}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">上次爬取</p>
                <p className="text-sm">
                  {status.last_crawl_time 
                    ? dayjs(status.last_crawl_time).fromNow()
                    : '未爬取'
                  }
                </p>
              </div>
            </div>
          ) : null}
        </div>

        {/* 手动触发卡片 */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">手动触发</h2>
          <p className="text-gray-600 mb-4">点击按钮立即执行爬虫和摘要生成任务</p>
          <button
            onClick={() => runJobMutation.mutate()}
            disabled={runJobMutation.isPending}
            className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {runJobMutation.isPending ? '执行中...' : '立即执行任务'}
          </button>
          {runJobMutation.isSuccess && (
            <p className="text-green-600 mt-2 text-sm">✅ 任务已提交</p>
          )}
        </div>
      </div>

      {/* 爬虫日志 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">最近的爬虫日志</h2>
        {!logs || logs.length === 0 ? (
          <p className="text-gray-600">暂无日志</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-gray-600">
                  <th className="text-left py-2 px-2">公众号ID</th>
                  <th className="text-left py-2 px-2">状态</th>
                  <th className="text-left py-2 px-2">文章数</th>
                  <th className="text-left py-2 px-2">耗时(秒)</th>
                  <th className="text-left py-2 px-2">执行时间</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log: any) => (
                  <tr key={log.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-2">{log.account_id}</td>
                    <td className="py-3 px-2">
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${
                        log.status === 'success' 
                          ? 'bg-green-100 text-green-700'
                          : 'bg-red-100 text-red-700'
                      }`}>
                        {log.status}
                      </span>
                    </td>
                    <td className="py-3 px-2">{log.article_count}</td>
                    <td className="py-3 px-2">{log.duration_seconds || '-'}</td>
                    <td className="py-3 px-2 text-gray-600">
                      {dayjs(log.run_at).format('YYYY-MM-DD HH:mm:ss')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
