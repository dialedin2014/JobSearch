/**
 * Dream job description form component.
 */

import React, { useState } from 'react';
import apiService from '../services/api';

interface DreamJobFormProps {
  onSubmitSuccess?: (dreamJobId: string) => void;
  onSubmitError?: (error: string) => void;
}

const MIN_LENGTH = 50;

export default function DreamJobForm({ onSubmitSuccess, onSubmitError }: DreamJobFormProps) {
  const [description, setDescription] = useState('');
  const [desiredRole, setDesiredRole] = useState('');
  const [desiredIndustry, setDesiredIndustry] = useState('');
  const [desiredCompanyType, setDesiredCompanyType] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const characterCount = description.length;
  const isValid = characterCount >= MIN_LENGTH;
  const remaining = MIN_LENGTH - characterCount;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!isValid) {
      setError(`Description must be at least ${MIN_LENGTH} characters.`);
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const response = await apiService.post<any>('/api/v1/dream-jobs', {
        description,
        desired_role: desiredRole || null,
        desired_industry: desiredIndustry || null,
        desired_company_type: desiredCompanyType || null,
      });

      if (onSubmitSuccess) {
        onSubmitSuccess(response.id);
      }

      // Clear form
      setDescription('');
      setDesiredRole('');
      setDesiredIndustry('');
      setDesiredCompanyType('');
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to save dream job. Please try again.';
      setError(errorMessage);
      if (onSubmitError) {
        onSubmitError(errorMessage);
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">Describe Your Dream Job</h2>
      <p className="text-gray-600 mb-6">
        Tell us about your ideal career position. Be specific about the role, responsibilities, and environment you're seeking.
      </p>

      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
            Dream Job Description *
          </label>
          <textarea
            id="description"
            rows={8}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Example: I want to become a Senior AI/ML Engineer at a healthcare technology company, working on machine learning models that improve patient outcomes. I'd like to lead a small team, collaborate with medical professionals, and have the opportunity to publish research..."
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
              !isValid && characterCount > 0 ? 'border-red-300' : 'border-gray-300'
            }`}
            disabled={submitting}
          />
          <div className="flex justify-between items-center mt-2">
            <span className={`text-sm ${isValid ? 'text-gray-500' : 'text-red-500'}`}>
              {characterCount} / {MIN_LENGTH} characters minimum
            </span>
            {!isValid && characterCount > 0 && (
              <span className="text-sm text-red-500">{remaining} more needed</span>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label htmlFor="desired-role" className="block text-sm font-medium text-gray-700 mb-2">
              Desired Role (Optional)
            </label>
            <input
              id="desired-role"
              type="text"
              value={desiredRole}
              onChange={(e) => setDesiredRole(e.target.value)}
              placeholder="e.g., Senior ML Engineer"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={submitting}
            />
          </div>

          <div>
            <label htmlFor="desired-industry" className="block text-sm font-medium text-gray-700 mb-2">
              Desired Industry (Optional)
            </label>
            <input
              id="desired-industry"
              type="text"
              value={desiredIndustry}
              onChange={(e) => setDesiredIndustry(e.target.value)}
              placeholder="e.g., Healthcare Technology"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={submitting}
            />
          </div>
        </div>

        <div className="mb-6">
          <label htmlFor="company-type" className="block text-sm font-medium text-gray-700 mb-2">
            Company Type (Optional)
          </label>
          <select
            id="company-type"
            value={desiredCompanyType}
            onChange={(e) => setDesiredCompanyType(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={submitting}
          >
            <option value="">Select...</option>
            <option value="startup">Startup</option>
            <option value="scale-up">Scale-up</option>
            <option value="enterprise">Enterprise</option>
            <option value="non-profit">Non-profit</option>
            <option value="government">Government</option>
            <option value="remote-first">Remote-first</option>
          </select>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        <button
          type="submit"
          disabled={!isValid || submitting}
          className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
            !isValid || submitting
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          {submitting ? 'Saving...' : 'Save Dream Job'}
        </button>
      </form>
    </div>
  );
}
