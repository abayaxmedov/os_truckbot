import { Icon } from "@/components/Icon";

/** Refined placeholder shown when a product has no image. */
export function Placeholder({ icon = "wrench", size = 40 }: { icon?: string; size?: number }) {
  return (
    <div className="thumb-ph">
      <Icon name={icon} size={size} strokeWidth={1.25} style={{ opacity: 0.5 }} />
    </div>
  );
}
