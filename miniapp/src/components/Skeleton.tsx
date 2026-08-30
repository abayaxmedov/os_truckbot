export function Skel({
  w = "100%",
  h = 14,
  r = 8,
  style,
}: {
  w?: number | string;
  h?: number | string;
  r?: number;
  style?: React.CSSProperties;
}) {
  return <div className="skel" style={{ width: w, height: h, borderRadius: r, ...style }} />;
}

export function SkeletonGrid({ count = 6 }: { count?: number }) {
  return (
    <div className="grid">
      {Array.from({ length: count }).map((_, i) => (
        <div className="card" key={i} style={{ overflow: "hidden" }}>
          <Skel w="100%" h={0} r={0} style={{ aspectRatio: "1 / 1", height: "auto" }} />
          <div style={{ padding: "10px 12px 13px", display: "flex", flexDirection: "column", gap: 8 }}>
            <Skel w="90%" h={12} />
            <Skel w="55%" h={12} />
            <Skel w="45%" h={16} style={{ marginTop: 4 }} />
          </div>
        </div>
      ))}
    </div>
  );
}

export function SkeletonList({ count = 5 }: { count?: number }) {
  return (
    <div className="list">
      {Array.from({ length: count }).map((_, i) => (
        <div className="list-row" key={i} style={{ cursor: "default" }}>
          <Skel w={40} h={40} r={10} />
          <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 7 }}>
            <Skel w="70%" h={12} />
            <Skel w="40%" h={11} />
          </div>
        </div>
      ))}
    </div>
  );
}

export function SkeletonCards({ count = 3, height = 90 }: { count?: number; height?: number }) {
  return (
    <div className="stack">
      {Array.from({ length: count }).map((_, i) => (
        <Skel key={i} w="100%" h={height} r={14} />
      ))}
    </div>
  );
}

export function SkeletonStats({ count = 4 }: { count?: number }) {
  return (
    <div className="stat-grid">
      {Array.from({ length: count }).map((_, i) => (
        <Skel key={i} w="100%" h={92} r={14} />
      ))}
    </div>
  );
}
