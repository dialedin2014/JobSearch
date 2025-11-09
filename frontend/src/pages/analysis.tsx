/**
 * Main analysis page integrating resume upload, dream job, and ally deduction.
 */

import React, { useState } from 'react';
import ResumeUpload from '../components/ResumeUpload';
import DreamJobForm from '../components/DreamJobForm';
import AllyTypesList from '../components/AllyTypesList';
import apiService from '../services/api';

interface AnalysisState {
  resumeId: string | null;
  dreamJobId: string | null;
  analysisId: string | null;
  analysisStatus: 'idle' | 'queued' | 'processing' | 'completed' | 'failed';
  allyTypes: any[];
  error: string | null;
}

export default function AnalysisPage() {
  const [state, setState] = useState<AnalysisState>({
    resumeId: null,
    dreamJobId: null,
    analysisId: null,
    analysisStatus: 'idle',
    allyTypes: [],
    error: null,
  });

  const [step, setStep] = useState<'upload' | 'dream-job' | 'results'>('upload');

  const handleResumeUploadSuccess = async (resumeId: string) => {
    setState(prev => ({ ...prev, resumeId, error: null }));
    
    // Poll for parsing status
    try {
      const parsedSuccessfully = await apiService.pollResumeStatus(resumeId);
      if (parsedSuccessfully) {
        setStep('dream-job');
      } else {
        setState(prev => ({ 
          ...prev, 
          error: 'Resume parsing failed. Please try uploading a different file.' 
        }));
      }
    } catch (err: any) {
      setState(prev => ({ 
        ...prev, 
        error: err.message || 'Failed to check resume status.' 
      }));
    }
  };

  const handleResumeUploadError = (error: string) => {
    setState(prev => ({ ...prev, error }));
  };

  const handleDreamJobSuccess = async (dreamJobId: string) => {
    setState(prev => ({ ...prev, dreamJobId, error: null }));
    
    // Start ally deduction analysis
    if (!state.resumeId) {
      setState(prev => ({ 
        ...prev, 
        error: 'Resume ID missing. Please upload your resume first.' 
      }));
      return;
    }

    try {
      const response = await apiService.post<any>('/api/v1/ally-deduction/analyze', {
        resume_id: state.resumeId,
        dream_job_id: dreamJobId,
      });

      const analysisId = response.analysis_id;
      setState(prev => ({ 
        ...prev, 
        analysisId, 
        analysisStatus: 'queued',
        error: null 
      }));

      setStep('results');

      // Poll for analysis completion
      const results = await apiService.pollAnalysisStatus(analysisId);
      if (results) {
        setState(prev => ({
          ...prev,
          analysisStatus: 'completed',
          allyTypes: results.ally_types || [],
        }));
      } else {
        setState(prev => ({
          ...prev,
          analysisStatus: 'failed',
          error: 'Analysis failed. Please try again.',
        }));
      }
    } catch (err: any) {
      setState(prev => ({
        ...prev,
        analysisStatus: 'failed',
        error: err.response?.data?.detail || 'Failed to start analysis.',
      }));
    }
  };

  const handleDreamJobError = (error: string) => {
    setState(prev => ({ ...prev, error }));
  };

  const handleStartOver = () => {
    setState({
      resumeId: null,
      dreamJobId: null,
      analysisId: null,
      analysisStatus: 'idle',
      allyTypes: [],
      error: null,
    });
    setStep('upload');
  };

  return (
    <div className="min-h-screen bg-gray-100 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Dream Job Ally Finder</h1>
          <p className="text-lg text-gray-600">
            Discover the professionals who can help you achieve your career goals
          </p>
        </header>

        {/* Progress Steps */}
        <div className="mb-12">
          <div className="flex items-center justify-center space-x-4">
            <div className="flex items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
                step === 'upload' 
                  ? 'bg-blue-600 text-white' 
                  : state.resumeId 
                    ? 'bg-green-500 text-white' 
                    : 'bg-gray-300 text-gray-600'
              }`}>
                1
              </div>
              <span className="ml-2 text-sm font-medium">Upload Resume</span>
            </div>
            
            <div className="w-16 h-1 bg-gray-300">
              <div 
                className={`h-full transition-all ${state.resumeId ? 'bg-green-500' : 'bg-gray-300'}`}
                style={{ width: state.resumeId ? '100%' : '0%' }}
              />
            </div>

            <div className="flex items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
                step === 'dream-job' 
                  ? 'bg-blue-600 text-white' 
                  : state.dreamJobId 
                    ? 'bg-green-500 text-white' 
                    : 'bg-gray-300 text-gray-600'
              }`}>
                2
              </div>
              <span className="ml-2 text-sm font-medium">Dream Job</span>
            </div>

            <div className="w-16 h-1 bg-gray-300">
              <div 
                className={`h-full transition-all ${state.dreamJobId ? 'bg-green-500' : 'bg-gray-300'}`}
                style={{ width: state.dreamJobId ? '100%' : '0%' }}
              />
            </div>

            <div className="flex items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
                step === 'results' 
                  ? 'bg-blue-600 text-white' 
                  : state.analysisStatus === 'completed' 
                    ? 'bg-green-500 text-white' 
                    : 'bg-gray-300 text-gray-600'
              }`}>
                3
              </div>
              <span className="ml-2 text-sm font-medium">Find Allies</span>
            </div>
          </div>
        </div>

        {/* Error Display */}
        {state.error && (
          <div className="mb-6 max-w-2xl mx-auto p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">{state.error}</p>
          </div>
        )}

        {/* Step Content */}
        {step === 'upload' && (
          <ResumeUpload 
            onUploadSuccess={handleResumeUploadSuccess}
            onUploadError={handleResumeUploadError}
          />
        )}

        {step === 'dream-job' && (
          <DreamJobForm 
            onSubmitSuccess={handleDreamJobSuccess}
            onSubmitError={handleDreamJobError}
          />
        )}

        {step === 'results' && (
          <div>
            {(state.analysisStatus === 'queued' || state.analysisStatus === 'processing') && (
              <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md text-center">
                <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
                <h3 className="text-xl font-semibold mb-2">Analyzing Your Profile</h3>
                <p className="text-gray-600">
                  Our AI is finding the perfect allies to help you reach your dream job...
                </p>
              </div>
            )}

            {state.analysisStatus === 'completed' && (
              <>
                <AllyTypesList allyTypes={state.allyTypes} loading={false} />
                <div className="mt-8 text-center">
                  <button
                    onClick={handleStartOver}
                    className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                  >
                    Start New Analysis
                  </button>
                </div>
              </>
            )}

            {state.analysisStatus === 'failed' && (
              <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md text-center">
                <div className="text-red-600 mb-4">
                  <svg className="w-16 h-16 mx-auto" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2">Analysis Failed</h3>
                <p className="text-gray-600 mb-6">{state.error || 'Something went wrong. Please try again.'}</p>
                <button
                  onClick={handleStartOver}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Try Again
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
