// Site-wide copyright footer.
export function Footer({ bordered = true }: { bordered?: boolean }) {
  return (
    <footer
      className={`mt-10 pt-4 text-center text-xs text-content-faint ${
        bordered ? "border-t border-border" : ""
      }`}
    >
      © {new Date().getFullYear()} Trackable. All rights reserved.
    </footer>
  );
}
