import { useState } from "react";
import { Checkbox } from "@/components/ui/checkbox";
import { toast } from "sonner";
import axios from "axios";
import { CheckCircle } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Logo = () => (
  <div className="logo-container">
    <img src="/logo.png" alt="Nexovent Labs" className="logo-image" />
    <span className="logo-text">
      <span className="orange">Nexovent</span>
      <span className="black"> Labs</span>
    </span>
  </div>
);

const ClientForm = () => {
  const [formData, setFormData] = useState({
    name: "",
    business_name: "",
    mobile_number: "",
    email: "",
    agreed_to_terms: false,
  });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSendingGif, setShowSendingGif] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const validate = () => {
    const newErrors = {};
    if (!formData.name.trim()) newErrors.name = "Name is required";
    if (!formData.business_name.trim()) newErrors.business_name = "Business name is required";
    if (!formData.mobile_number.trim()) {
      newErrors.mobile_number = "Mobile number is required";
    } else if (!/^[\d\s\-\+\(\)]{7,20}$/.test(formData.mobile_number)) {
      newErrors.mobile_number = "Please enter a valid mobile number";
    }
    if (!formData.email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = "Please enter a valid email address";
    }
    if (!formData.agreed_to_terms) newErrors.agreed_to_terms = "You must agree to the terms";
    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const validationErrors = validate();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setIsSubmitting(true);
    setErrors({});

    try {
      await axios.post(`${API}/submissions`, formData);
      setIsSubmitting(false);
      setShowSendingGif(true);
      
      // Show gif for 3 seconds then show success message
      setTimeout(() => {
        setShowSendingGif(false);
        setIsSubmitted(true);
      }, 3000);
    } catch (error) {
      console.error("Submission error:", error);
      toast.error(error.response?.data?.detail || "Failed to submit form. Please try again.");
      setIsSubmitting(false);
    }
  };

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: null }));
    }
  };

  if (showSendingGif) {
    return (
      <div className="success-container">
        <div className="success-card" style={{ padding: "60px 48px" }}>
          <Logo />
          <img 
            src="/send.gif" 
            alt="Sending..." 
            style={{ 
              width: "150px", 
              height: "150px", 
              margin: "20px auto",
              display: "block"
            }} 
          />
          <p style={{ color: "#71717a", fontSize: "16px", marginTop: "16px" }}>
            Sending your information...
          </p>
        </div>
      </div>
    );
  }

  if (isSubmitted) {
    return (
      <div className="success-container">
        <div className="success-card" data-testid="success-message">
          <Logo />
          <div className="success-icon">
            <CheckCircle size={44} color="white" />
          </div>
          <h1>Thank You!</h1>
          <p>
            Your information has been submitted successfully.<br />
            We will contact you within <span className="highlight">7 to 8 hours</span>.
          </p>
          <button 
            className="submit-btn" 
            onClick={() => window.open("https://nexovent-labs.vercel.app/", "_blank")}
            style={{ marginTop: "16px" }}
          >
            Visit Our Website
          </button>
          <button 
            className="back-btn" 
            onClick={() => {
              setIsSubmitted(false);
              setFormData({ name: "", business_name: "", mobile_number: "", email: "", agreed_to_terms: false });
            }}
            data-testid="submit-another-btn"
          >
            Submit Another Response
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="form-container">
      <div className="form-card">
        <Logo />
        <div className="form-header">
          <h1>Client Intake Form</h1>
          <p>Please fill in your details below</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-field">
            <label htmlFor="name">Your Name *</label>
            <input
              id="name"
              type="text"
              placeholder="Enter your full name"
              value={formData.name}
              onChange={(e) => handleChange("name", e.target.value)}
              data-testid="name-input"
            />
            {errors.name && <p className="error-text">{errors.name}</p>}
          </div>

          <div className="form-field">
            <label htmlFor="business_name">Business Name *</label>
            <input
              id="business_name"
              type="text"
              placeholder="Enter your business name"
              value={formData.business_name}
              onChange={(e) => handleChange("business_name", e.target.value)}
              data-testid="business-name-input"
            />
            {errors.business_name && <p className="error-text">{errors.business_name}</p>}
          </div>

          <div className="form-field">
            <label htmlFor="mobile_number">Mobile Number *</label>
            <input
              id="mobile_number"
              type="tel"
              placeholder="Enter your mobile number"
              value={formData.mobile_number}
              onChange={(e) => handleChange("mobile_number", e.target.value)}
              data-testid="mobile-input"
            />
            {errors.mobile_number && <p className="error-text">{errors.mobile_number}</p>}
          </div>

          <div className="form-field">
            <label htmlFor="email">Email Address *</label>
            <input
              id="email"
              type="email"
              placeholder="Enter your email address"
              value={formData.email}
              onChange={(e) => handleChange("email", e.target.value)}
              data-testid="email-input"
            />
            {errors.email && <p className="error-text">{errors.email}</p>}
          </div>

          <div className="terms-container">
            <Checkbox
              id="terms"
              checked={formData.agreed_to_terms}
              onCheckedChange={(checked) => handleChange("agreed_to_terms", checked)}
              data-testid="terms-checkbox"
            />
            <label htmlFor="terms" className="terms-text">
              I agree to the <span className="terms-link">Terms and Conditions</span> and consent to the collection and processing of my personal information as described in the <span className="terms-link">Privacy Policy</span>.
            </label>
          </div>
          {errors.agreed_to_terms && <p className="error-text" style={{ marginTop: "-16px", marginBottom: "16px" }}>{errors.agreed_to_terms}</p>}

          <button
            type="submit"
            className="submit-btn"
            disabled={isSubmitting}
            data-testid="submit-btn"
          >
            {isSubmitting ? "Submitting..." : "Submit"}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ClientForm;
