import { cn } from "@/lib/utils";

const sizeMap = {
  sm: {
    frame: "p-1.5 rounded-2xl",
    icon: "w-8 h-8",
    text: "text-xl sm:text-2xl",
    gap: "gap-2.5",
  },
  md: {
    frame: "p-2 rounded-[1.35rem]",
    icon: "w-10 h-10",
    text: "text-2xl sm:text-3xl",
    gap: "gap-3",
  },
  lg: {
    frame: "p-2.5 rounded-[1.6rem]",
    icon: "w-12 h-12 sm:w-14 sm:h-14",
    text: "text-4xl sm:text-5xl",
    gap: "gap-3.5",
  },
};

export const BrandHeading = ({
  label = "Goal Kick",
  size = "md",
  className,
  textClassName,
  testId = "brand-heading",
}) => {
  const config = sizeMap[size] || sizeMap.md;

  return (
    <div className={cn("inline-flex items-center", config.gap, className)} data-testid={testId}>
      <div
        className={cn(
          "bg-white/90 border-2 border-sky-200 shadow-[0_14px_35px_rgba(14,165,233,0.16)]",
          config.frame,
        )}
      >
        <img
          src="/gemini-svg.svg"
          alt="Goal Kick icon"
          className={cn("object-contain", config.icon)}
          data-testid={`${testId}-icon`}
        />
      </div>
      <span
        className={cn("font-black tracking-tight text-slate-800 leading-none", config.text, textClassName)}
        data-testid={`${testId}-text`}
      >
        {label}
      </span>
    </div>
  );
};