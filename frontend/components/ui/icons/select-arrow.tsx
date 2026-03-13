import React from 'react';

export default function SelectArrow({
  ...otherProps
}: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      width="21"
      height="12"
      viewBox="0 0 21 12"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      {...otherProps}
    >
      <path
        d="M19 1.87695L10.25 10.0491L1.5 1.87695"
        stroke="white"
        strokeWidth="2.42424"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
