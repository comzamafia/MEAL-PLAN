export function HowItWorks() {
  const steps = [
    {
      number: "01",
      title: "Choose Your Meals",
      description:
        "Browse our weekly rotating menu and select the meals you want. Mix and match any combination.",
      icon: "🍽️",
    },
    {
      number: "02",
      title: "We Cook Fresh",
      description:
        "Our chefs prepare your meals fresh on Saturday using premium ingredients. Never frozen.",
      icon: "👨‍🍳",
    },
    {
      number: "03",
      title: "Sunday Delivery",
      description:
        "Meals arrive at your door every Sunday between 3-5 PM, ready for the week ahead.",
      icon: "🚗",
    },
    {
      number: "04",
      title: "Heat & Enjoy",
      description:
        "Just 3 minutes in the microwave and you have a restaurant-quality meal. Simple as that.",
      icon: "✨",
    },
  ];

  return (
    <section id="how-it-works" className="py-16 md:py-24 bg-white">
      <div className="container px-4 md:px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">
            How It Works
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Getting healthy, delicious meals has never been easier.
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          {steps.map((step, index) => (
            <div key={index} className="relative">
              {/* Connector Line */}
              {index < steps.length - 1 && (
                <div className="hidden lg:block absolute top-12 left-1/2 w-full h-0.5 bg-green-200" />
              )}

              <div className="relative flex flex-col items-center text-center">
                <div className="flex h-24 w-24 items-center justify-center rounded-full bg-green-100 text-4xl mb-4 relative z-10">
                  {step.icon}
                </div>
                <span className="text-sm font-semibold text-green-600 mb-2">
                  STEP {step.number}
                </span>
                <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
                <p className="text-gray-600 text-sm">{step.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
