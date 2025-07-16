'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  StarIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  ChartBarIcon,
  DocumentTextIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Generation, GenerationStatus } from '@/types';

interface EvaluationCriteria {
  name: string;
  description: string;
  score: number;
  weight: number;
}

interface EvaluationData {
  generation_id: string;
  criteria: EvaluationCriteria[];
  overall_score: number;
  comments: string;
  hallucination_detected: boolean;
  issues: string[];
}

export default function EvaluationsPage() {
  const router = useRouter();
  const [currentGenerationIndex, setCurrentGenerationIndex] = useState(0);
  const [evaluationData, setEvaluationData] = useState<EvaluationData>({
    generation_id: '',
    criteria: [
      { name: 'Accuracy', description: 'Information is factually correct', score: 0, weight: 0.3 },
      { name: 'Relevance', description: 'Response addresses the question appropriately', score: 0, weight: 0.25 },
      { name: 'Clarity', description: 'Response is clear and easy to understand', score: 0, weight: 0.2 },
      { name: 'Completeness', description: 'Response covers all aspects of the question', score: 0, weight: 0.15 },
      { name: 'Helpfulness', description: 'Response is useful and actionable', score: 0, weight: 0.1 },
    ],
    overall_score: 0,
    comments: '',
    hallucination_detected: false,
    issues: [],
  });

  // Mock generations for evaluation
  const generationsToEvaluate: Generation[] = [
    {
      id: '1',
      element_id: '1',
      element_name: 'Customer FAQ Template',
      status: GenerationStatus.COMPLETED,
      input_data: {
        context: 'Our return policy allows customers to return products within 30 days of purchase for a full refund. Products must be in original condition.',
        question: 'Can I return my product after 2 weeks?'
      },
      output_text: 'Yes, you can return your product after 2 weeks. Our return policy allows returns within 30 days of purchase for a full refund, as long as the product is in original condition.',
      model_used: 'gpt-4-turbo',
      tokens_used: 245,
      execution_time: 2.3,
      cost: 0.012,
      project_id: '1',
      created_at: '2024-12-25T14:20:00Z',
      updated_at: '2024-12-25T14:20:00Z',
      error_message: null
    },
    {
      id: '2',
      element_id: '1',
      element_name: 'Customer FAQ Template',
      status: GenerationStatus.COMPLETED,
      input_data: {
        context: 'Shipping is free for orders over $50. Standard shipping takes 3-5 business days.',
        question: 'How long does shipping take?'
      },
      output_text: 'Standard shipping typically takes 3-5 business days. If your order is over $50, shipping is completely free! For orders under $50, standard shipping rates apply.',
      model_used: 'gpt-4-turbo',
      tokens_used: 189,
      execution_time: 1.8,
      cost: 0.009,
      project_id: '1',
      created_at: '2024-12-25T14:15:00Z',
      updated_at: '2024-12-25T14:15:00Z',
      error_message: null
    }
  ];

  const currentGeneration = generationsToEvaluate[currentGenerationIndex];

  const updateCriteriaScore = (index: number, score: number) => {
    const newCriteria = [...evaluationData.criteria];
    newCriteria[index].score = score;
    
    // Calculate overall score based on weighted average
    const totalWeight = newCriteria.reduce((sum, c) => sum + c.weight, 0);
    const weightedSum = newCriteria.reduce((sum, c) => sum + (c.score * c.weight), 0);
    const overallScore = totalWeight > 0 ? weightedSum / totalWeight : 0;

    setEvaluationData(prev => ({
      ...prev,
      criteria: newCriteria,
      overall_score: overallScore,
      generation_id: currentGeneration.id
    }));
  };

  const toggleIssue = (issue: string) => {
    setEvaluationData(prev => ({
      ...prev,
      issues: prev.issues.includes(issue)
        ? prev.issues.filter(i => i !== issue)
        : [...prev.issues, issue]
    }));
  };

  const submitEvaluation = async () => {
    try {
      // Mock API call - replace with actual implementation
      console.log('Submitting evaluation:', evaluationData);
      
      // Move to next generation or complete
      if (currentGenerationIndex < generationsToEvaluate.length - 1) {
        setCurrentGenerationIndex(prev => prev + 1);
        // Reset evaluation data for next generation
        setEvaluationData(prev => ({
          ...prev,
          criteria: prev.criteria.map(c => ({ ...c, score: 0 })),
          overall_score: 0,
          comments: '',
          hallucination_detected: false,
          issues: [],
          generation_id: generationsToEvaluate[currentGenerationIndex + 1].id
        }));
      } else {
        // All evaluations complete
        router.push('/evaluations/complete');
      }
    } catch (error) {
      console.error('Failed to submit evaluation:', error);
    }
  };

  const skipGeneration = () => {
    if (currentGenerationIndex < generationsToEvaluate.length - 1) {
      setCurrentGenerationIndex(prev => prev + 1);
    }
  };

  const previousGeneration = () => {
    if (currentGenerationIndex > 0) {
      setCurrentGenerationIndex(prev => prev - 1);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 4) return 'text-green-600';
    if (score >= 3) return 'text-yellow-600';
    if (score >= 2) return 'text-orange-600';
    return 'text-red-600';
  };

  const getOverallScoreColor = (score: number) => {
    if (score >= 4) return 'bg-green-100 text-green-800';
    if (score >= 3) return 'bg-yellow-100 text-yellow-800';
    if (score >= 2) return 'bg-orange-100 text-orange-800';
    return 'bg-red-100 text-red-800';
  };

  const commonIssues = [
    'Factual inaccuracy',
    'Irrelevant information',
    'Unclear language',
    'Missing context',
    'Inappropriate tone',
    'Hallucinated details',
  ];

  return (
    <DashboardLayout title="Content Evaluation">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Progress Header */}
        <div className="bg-white shadow rounded-lg mb-6 p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Quality Assessment</h1>
              <p className="text-gray-600">
                Evaluating generation {currentGenerationIndex + 1} of {generationsToEvaluate.length}
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getOverallScoreColor(evaluationData.overall_score)}`}>
                Overall Score: {evaluationData.overall_score.toFixed(1)}/5.0
              </span>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${((currentGenerationIndex + 1) / generationsToEvaluate.length) * 100}%` }}
            />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
          {/* Main Evaluation Interface */}
          <div className="lg:col-span-3 space-y-6">
            {/* Generation Content */}
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-medium text-gray-900">Generation to Evaluate</h2>
                <div className="flex items-center space-x-2 text-sm text-gray-500">
                  <SparklesIcon className="h-4 w-4" />
                  <span>{currentGeneration.element_name}</span>
                </div>
              </div>

              {/* Input Context */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-700 mb-2">Input Context</h3>
                <div className="bg-gray-50 border border-gray-200 rounded-md p-3">
                  <p className="text-sm text-gray-700 mb-2">
                    <strong>Context:</strong> {currentGeneration.input_data.context}
                  </p>
                  <p className="text-sm text-gray-700">
                    <strong>Question:</strong> {currentGeneration.input_data.question}
                  </p>
                </div>
              </div>

              {/* Generated Output */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Generated Response</h3>
                <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                  <p className="text-gray-800 leading-relaxed">
                    {currentGeneration.output_text}
                  </p>
                </div>
              </div>
            </div>

            {/* Evaluation Criteria */}
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Evaluation Criteria</h2>
              <div className="space-y-6">
                {evaluationData.criteria.map((criteria, index) => (
                  <div key={criteria.name}>
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <h3 className="text-sm font-medium text-gray-900">{criteria.name}</h3>
                        <p className="text-xs text-gray-500">{criteria.description}</p>
                      </div>
                      <span className={`text-lg font-semibold ${getScoreColor(criteria.score)}`}>
                        {criteria.score}/5
                      </span>
                    </div>
                    <div className="flex space-x-2">
                      {[1, 2, 3, 4, 5].map((score) => (
                        <button
                          key={score}
                          onClick={() => updateCriteriaScore(index, score)}
                          className={`w-8 h-8 rounded-full border-2 flex items-center justify-center text-sm font-medium transition-colors ${
                            criteria.score >= score
                              ? 'border-blue-500 bg-blue-500 text-white'
                              : 'border-gray-300 text-gray-500 hover:border-blue-300'
                          }`}
                        >
                          {score}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Issues and Comments */}
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Quality Issues</h2>
              
              {/* Hallucination Check */}
              <div className="mb-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={evaluationData.hallucination_detected}
                    onChange={(e) => setEvaluationData(prev => ({ ...prev, hallucination_detected: e.target.checked }))}
                    className="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">
                    <ExclamationTriangleIcon className="h-4 w-4 text-red-500 inline mr-1" />
                    Hallucination detected (factually incorrect information)
                  </span>
                </label>
              </div>

              {/* Common Issues */}
              <div className="mb-4">
                <h3 className="text-sm font-medium text-gray-700 mb-2">Common Issues</h3>
                <div className="grid grid-cols-2 gap-2">
                  {commonIssues.map((issue) => (
                    <label key={issue} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={evaluationData.issues.includes(issue)}
                        onChange={() => toggleIssue(issue)}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <span className="ml-2 text-sm text-gray-700">{issue}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Comments */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Additional Comments
                </label>
                <textarea
                  rows={3}
                  value={evaluationData.comments}
                  onChange={(e) => setEvaluationData(prev => ({ ...prev, comments: e.target.value }))}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
                  placeholder="Add any specific feedback or observations..."
                />
              </div>
            </div>

            {/* Navigation */}
            <div className="flex justify-between">
              <button
                onClick={previousGeneration}
                disabled={currentGenerationIndex === 0}
                className={`inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium ${
                  currentGenerationIndex === 0
                    ? 'text-gray-400 cursor-not-allowed'
                    : 'text-gray-700 bg-white hover:bg-gray-50'
                }`}
              >
                <ChevronLeftIcon className="h-4 w-4 mr-2" />
                Previous
              </button>

              <div className="flex space-x-3">
                <button
                  onClick={skipGeneration}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                >
                  Skip
                </button>
                <button
                  onClick={submitEvaluation}
                  className="inline-flex items-center px-6 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                >
                  {currentGenerationIndex === generationsToEvaluate.length - 1 ? 'Complete' : 'Next'}
                  <ChevronRightIcon className="h-4 w-4 ml-2" />
                </button>
              </div>
            </div>
          </div>

          {/* Context Panel */}
          <div className="lg:col-span-2 space-y-6">
            {/* Source Context */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Source Context</h3>
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Element Used</h4>
                  <div className="flex items-center p-3 bg-gray-50 rounded-lg">
                    <DocumentTextIcon className="h-5 w-5 text-gray-400 mr-3" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">{currentGeneration.element_name}</p>
                      <p className="text-xs text-gray-500">Prompt Template</p>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Generation Metrics</h4>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="text-center p-2 bg-gray-50 rounded">
                      <p className="text-xs text-gray-500">Tokens</p>
                      <p className="text-sm font-medium">{currentGeneration.tokens_used}</p>
                    </div>
                    <div className="text-center p-2 bg-gray-50 rounded">
                      <p className="text-xs text-gray-500">Time</p>
                      <p className="text-sm font-medium">{currentGeneration.execution_time}s</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Evaluation Guidelines */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Evaluation Guidelines</h3>
              <div className="space-y-3">
                <div className="flex">
                  <StarIcon className="h-5 w-5 text-yellow-500 mr-2 mt-0.5" />
                  <div className="text-sm text-gray-600">
                    <p className="font-medium">Scoring Scale</p>
                    <p>5 = Excellent, 4 = Good, 3 = Average, 2 = Poor, 1 = Very Poor</p>
                  </div>
                </div>
                <div className="flex">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2 mt-0.5" />
                  <div className="text-sm text-gray-600">
                    <p className="font-medium">Accuracy Check</p>
                    <p>Verify facts against source context and domain knowledge</p>
                  </div>
                </div>
                <div className="flex">
                  <InformationCircleIcon className="h-5 w-5 text-blue-500 mr-2 mt-0.5" />
                  <div className="text-sm text-gray-600">
                    <p className="font-medium">Relevance Assessment</p>
                    <p>Ensure response directly addresses the input question</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Quality Checklist */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Quality Checklist</h3>
              <div className="space-y-2">
                <div className="flex items-center">
                  <input type="checkbox" className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded" />
                  <span className="ml-2 text-sm text-gray-700">Response uses provided context</span>
                </div>
                <div className="flex items-center">
                  <input type="checkbox" className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded" />
                  <span className="ml-2 text-sm text-gray-700">Tone is appropriate</span>
                </div>
                <div className="flex items-center">
                  <input type="checkbox" className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded" />
                  <span className="ml-2 text-sm text-gray-700">No contradictory information</span>
                </div>
                <div className="flex items-center">
                  <input type="checkbox" className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded" />
                  <span className="ml-2 text-sm text-gray-700">Grammar and spelling correct</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
} 