import React from 'react'
import { Link } from 'react-router-dom'

export const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600">
      <div className="max-w-5xl mx-auto px-4 py-20 text-white">
        <div className="text-center mb-16">
          <h1 className="text-5xl md:text-6xl font-bold mb-4">📰 WeChat Summary</h1>
          <p className="text-xl md:text-2xl text-blue-100 mb-8">
            自动爬取微信公众号文章，智能生成摘要
          </p>
          <Link 
            to="/feed"
            className="inline-block px-8 py-4 bg-white text-blue-600 font-semibold rounded-lg hover:shadow-lg transition-shadow"
          >
            开始阅读 →
          </Link>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-16">
          <div className="bg-white bg-opacity-10 rounded-lg p-6 backdrop-blur">
            <h3 className="text-2xl font-semibold mb-3">🔄 自动更新</h3>
            <p className="text-blue-100">每天定时自动爬取追踪公众号的最新文章</p>
          </div>
          <div className="bg-white bg-opacity-10 rounded-lg p-6 backdrop-blur">
            <h3 className="text-2xl font-semibold mb-3">✨ 智能摘要</h3>
            <p className="text-blue-100">使用LLM AI生成高质量文章摘要</p>
          </div>
          <div className="bg-white bg-opacity-10 rounded-lg p-6 backdrop-blur">
            <h3 className="text-2xl font-semibold mb-3">📊 数据聚合</h3>
            <p className="text-blue-100">汇总展示，支持按日期和公众号筛选</p>
          </div>
        </div>

        <div className="bg-white bg-opacity-10 rounded-lg p-8 backdrop-blur text-center">
          <h2 className="text-3xl font-semibold mb-4">开始使用</h2>
          <div className="grid md:grid-cols-3 gap-4 mb-6">
            <div>
              <p className="text-blue-100 mb-2">第一步</p>
              <p className="font-semibold">添加公众号</p>
            </div>
            <div>
              <p className="text-blue-100 mb-2">第二步</p>
              <p className="font-semibold">等待爬虫更新</p>
            </div>
            <div>
              <p className="text-blue-100 mb-2">第三步</p>
              <p className="font-semibold">阅读摘要</p>
            </div>
          </div>
          <Link 
            to="/accounts"
            className="inline-block px-6 py-2 bg-white text-blue-600 font-semibold rounded hover:shadow-md transition-shadow"
          >
            管理公众号
          </Link>
        </div>
      </div>
    </div>
  )
}
