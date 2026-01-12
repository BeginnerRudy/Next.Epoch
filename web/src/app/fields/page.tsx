'use client';

import { useQuery } from '@tanstack/react-query';
import { getFields } from '@/lib/api';
import Link from 'next/link';
import { Tag, ChevronRight, Loader2, Info } from 'lucide-react';

// Map field IDs to likely arXiv categories
const fieldToCategoryMap: Record<string, string> = {
  'llm': 'cs.CL',  // Computation and Language
  'agents': 'cs.AI',  // Artificial Intelligence
  'vision': 'cs.CV',  // Computer Vision
  'robotics': 'cs.RO',  // Robotics
  'rl': 'cs.LG',  // Machine Learning
  'safety': 'cs.AI',  // AI Safety falls under AI
  'multimodal': 'cs.CV',  // Multimodal often intersects with CV
  'diffusion': 'cs.LG',  // Diffusion models are ML
  'retrieval': 'cs.IR',  // Information Retrieval
  'efficiency': 'cs.LG',  // Efficiency is ML
};

export default function FieldsPage() {
  const { data: fields, isLoading, error } = useQuery({
    queryKey: ['fields'],
    queryFn: getFields,
    retry: false,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <h3 className="font-medium text-red-800">Error loading fields</h3>
        <p className="text-sm text-red-700 mt-1">
          Could not load fields. Please try again later.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Fields</h1>
        <p className="text-gray-500 mt-1">
          Browse AI research and development by field
        </p>
      </div>

      {/* Info box about field mapping */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
        <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-sm text-blue-800">
            Fields are mapped to arXiv categories. Click a field to see related papers and repositories.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {fields?.map((field) => {
          const category = fieldToCategoryMap[field.id] || 'cs.AI';
          return (
            <Link
              key={field.id}
              href={`/content?category=${category}`}
              className="bg-white rounded-lg border border-gray-200 p-4 hover:border-primary-300 hover:shadow-md transition-all group"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-primary-100 text-primary-600">
                    <Tag className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
                      {field.name}
                    </h3>
                    {field.description && (
                      <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                        {field.description}
                      </p>
                    )}
                    <p className="text-xs text-gray-400 mt-1">
                      Category: {category}
                    </p>
                  </div>
                </div>
                <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-primary-600 transition-colors" />
              </div>
            </Link>
          );
        })}
      </div>

      {(!fields || fields.length === 0) && (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <Tag className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900">No fields yet</h3>
          <p className="text-gray-500 mt-1">
            Fields will appear here once content is categorized.
          </p>
        </div>
      )}
    </div>
  );
}
