import React from 'react';

export function CourseWidget({ dest }: { dest?: string }) {
  if (!dest) return null;
  return <div className="course-widget">Course to {dest}</div>;
}
