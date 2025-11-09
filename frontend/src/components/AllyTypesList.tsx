/**
 * Ally types list component with sorting and filtering.
 */

import React, { useState } from 'react';

interface AllyType {
  id: string;
  ally_type_name: string;
  confidence_score: number;
  selection_rationale: string;
  search_queries: {
    github?: string;
    twitter?: string;
    linkedin?: string;
  };
  engagement_strategy: string;
  rank: number;
}

interface AllyTypesListProps {
  allyTypes: AllyType[];
  loading?: boolean;
}

export default function AllyTypesList({ allyTypes, loading }: AllyTypesListProps) {
  const [sortBy, setSortBy] = useState<'rank' | 'confidence'>('rank');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  if (loading) {
    return (
      <div className="w-full max-w-4xl mx-auto p-6">
        <div className="animate-pulse space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white rounded-lg shadow-md p-6">
              <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
              <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-5/6"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (allyTypes.length === 0) {
    return (
      <div className="w-full max-w-4xl mx-auto p-6">
        <div className="bg-gray-50 rounded-lg p-8 text-center">
          <p className="text-gray-600">No ally types found. Try analyzing your resume and dream job first.</p>
        </div>
      </div>
    );
  }

  const sortedAllyTypes = [...allyTypes].sort((a, b) => {
    if (sortBy === 'rank') {
      return a.rank - b.rank;
    } else {
      return b.confidence_score - a.confidence_score;
    }
  });

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Your Professional Allies</h2>
        <div className="flex items-center space-x-2">
          <label className="text-sm text-gray-600">Sort by:</label>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'rank' | 'confidence')}
            className="px-3 py-1 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="rank">Priority</option>
            <option value="confidence">Confidence</option>
          </select>
        </div>
      </div>

      <div className="space-y-4">
        {sortedAllyTypes.map((ally) => (
          <div
            key={ally.id}
            className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow"
          >
            <div className="p-6">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 text-blue-800 font-semibold text-sm">
                      {ally.rank}
                    </span>
                    <h3 className="text-lg font-semibold text-gray-900">{ally.ally_type_name}</h3>
                  </div>
                </div>
                <div className="flex flex-col items-end space-y-1">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-500">Confidence:</span>
                    <span className="text-lg font-bold text-blue-600">
                      {(ally.confidence_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${ally.confidence_score * 100}%` }}
                    />
                  </div>
                </div>
              </div>

              <p className="text-gray-700 mb-4">{ally.selection_rationale}</p>

              <button
                onClick={() => toggleExpand(ally.id)}
                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                {expandedId === ally.id ? 'Hide Details ▲' : 'Show Search Queries & Strategy ▼'}
              </button>

              {expandedId === ally.id && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <div className="mb-4">
                    <h4 className="text-sm font-semibold text-gray-700 mb-2">Platform Search Queries:</h4>
                    <div className="space-y-2">
                      {ally.search_queries.github && (
                        <div className="flex items-start space-x-2 bg-gray-50 p-3 rounded">
                          <svg className="w-5 h-5 text-gray-700 mt-0.5" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                          </svg>
                          <div className="flex-1">
                            <p className="text-xs font-medium text-gray-700">GitHub:</p>
                            <code className="text-xs text-gray-600 break-all">{ally.search_queries.github}</code>
                          </div>
                        </div>
                      )}
                      {ally.search_queries.twitter && (
                        <div className="flex items-start space-x-2 bg-gray-50 p-3 rounded">
                          <svg className="w-5 h-5 text-blue-400 mt-0.5" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
                          </svg>
                          <div className="flex-1">
                            <p className="text-xs font-medium text-gray-700">Twitter/X:</p>
                            <code className="text-xs text-gray-600 break-all">{ally.search_queries.twitter}</code>
                          </div>
                        </div>
                      )}
                      {ally.search_queries.linkedin && (
                        <div className="flex items-start space-x-2 bg-gray-50 p-3 rounded">
                          <svg className="w-5 h-5 text-blue-700 mt-0.5" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                          </svg>
                          <div className="flex-1">
                            <p className="text-xs font-medium text-gray-700">LinkedIn:</p>
                            <code className="text-xs text-gray-600 break-all">{ally.search_queries.linkedin}</code>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  <div>
                    <h4 className="text-sm font-semibold text-gray-700 mb-2">Engagement Strategy:</h4>
                    <p className="text-sm text-gray-600 bg-blue-50 p-3 rounded">{ally.engagement_strategy}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
