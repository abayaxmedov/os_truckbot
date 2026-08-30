import type { ReactNode } from "react";

export function PageHeader({
  title,
  subtitle,
  action,
}: {
  title: string;
  subtitle?: string;
  action?: ReactNode;
}) {
  return (
    <div className="page-header">
      <div style={{ minWidth: 0 }}>
        <div className="ph-title">{title}</div>
        {subtitle && <div className="ph-sub">{subtitle}</div>}
      </div>
      {action}
    </div>
  );
}
