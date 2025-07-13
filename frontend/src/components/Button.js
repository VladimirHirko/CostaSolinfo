// components/Button.js
const Button = ({ children, onClick, className = '' }) => (
  <button onClick={onClick} className={`btn-style ${className}`}>
    {children}
  </button>
);
export default Button;
