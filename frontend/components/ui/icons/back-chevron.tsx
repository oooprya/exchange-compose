export default function BackChevron({
  ...otherProps
}: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      width="12"
      height="20"
      viewBox="0 0 12 20"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      {...otherProps}
    >
      <path
        d="M10.1719 18.75L1.99972 10L10.1719 1.25"
        stroke="white"
        strokeWidth="2.42424"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
