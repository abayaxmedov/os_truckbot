// Official TRUCK CENTER logo. Assets live in /public (logo.png, logo-white.png,
// logo-mark.png, logo-mark-white.png). `variant="auto"` swaps navy/white by theme.

export function Logo({
  variant = "auto",
  mark = false,
  height = 32,
}: {
  variant?: "auto" | "navy" | "white";
  mark?: boolean;
  height?: number;
}) {
  const base = mark ? "logo-mark" : "logo";
  const style: React.CSSProperties = { height, width: "auto" };
  if (variant === "navy") return <img src={`/${base}.png`} alt="TRUCK CENTER" style={style} />;
  if (variant === "white") return <img src={`/${base}-white.png`} alt="TRUCK CENTER" style={style} />;
  return (
    <span className="logo-auto" style={{ height }}>
      <img className="l-light" src={`/${base}.png`} alt="TRUCK CENTER" style={style} />
      <img className="l-dark" src={`/${base}-white.png`} alt="TRUCK CENTER" style={style} />
    </span>
  );
}
