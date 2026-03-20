import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Allergen Information & Food Safety | Wela Meal Plan",
  description: "Allergen information, dietary accommodations, and food safety practices at Wela Meal Plan.",
};

export default function AllergensPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container max-w-4xl mx-auto px-4 py-16">
        <h1 className="text-4xl font-bold mb-8">Allergen Information & Food Safety</h1>
        <p className="text-gray-600 mb-8">Last updated: March 2026</p>

        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-8">
          <p className="text-yellow-800 font-medium">
            Important: Our kitchen handles common allergens. While we take precautions,
            we cannot guarantee a completely allergen-free environment. If you have
            severe allergies, please consult with your healthcare provider before ordering.
          </p>
        </div>

        <div className="prose prose-gray max-w-none space-y-8">
          <section>
            <h2 className="text-2xl font-semibold mb-4">Common Allergens in Our Kitchen</h2>
            <p>
              Our kitchen prepares foods containing the following major allergens:
            </p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
              <div className="bg-white p-4 rounded-lg border text-center">
                <span className="text-2xl">🥜</span>
                <p className="font-medium mt-2">Peanuts</p>
              </div>
              <div className="bg-white p-4 rounded-lg border text-center">
                <span className="text-2xl">🌰</span>
                <p className="font-medium mt-2">Tree Nuts</p>
              </div>
              <div className="bg-white p-4 rounded-lg border text-center">
                <span className="text-2xl">🥛</span>
                <p className="font-medium mt-2">Dairy</p>
              </div>
              <div className="bg-white p-4 rounded-lg border text-center">
                <span className="text-2xl">🥚</span>
                <p className="font-medium mt-2">Eggs</p>
              </div>
              <div className="bg-white p-4 rounded-lg border text-center">
                <span className="text-2xl">🌾</span>
                <p className="font-medium mt-2">Gluten</p>
              </div>
              <div className="bg-white p-4 rounded-lg border text-center">
                <span className="text-2xl">🦐</span>
                <p className="font-medium mt-2">Shellfish</p>
              </div>
              <div className="bg-white p-4 rounded-lg border text-center">
                <span className="text-2xl">🐟</span>
                <p className="font-medium mt-2">Fish</p>
              </div>
              <div className="bg-white p-4 rounded-lg border text-center">
                <span className="text-2xl">🫘</span>
                <p className="font-medium mt-2">Soy</p>
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Dietary Labels on Our Menu</h2>
            <p>
              Each menu item displays applicable dietary labels to help you make informed choices:
            </p>
            <ul className="list-none pl-0 mt-4 space-y-3">
              <li className="flex items-center gap-3">
                <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">GF</span>
                <span><strong>Gluten-Free:</strong> Contains no gluten-containing ingredients</span>
              </li>
              <li className="flex items-center gap-3">
                <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">DF</span>
                <span><strong>Dairy-Free:</strong> Contains no milk or milk derivatives</span>
              </li>
              <li className="flex items-center gap-3">
                <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-medium">Halal</span>
                <span><strong>Halal:</strong> Prepared according to Islamic dietary guidelines</span>
              </li>
              <li className="flex items-center gap-3">
                <span className="bg-orange-100 text-orange-800 px-3 py-1 rounded-full text-sm font-medium">High Protein</span>
                <span><strong>High Protein:</strong> Contains 30g or more of protein per serving</span>
              </li>
              <li className="flex items-center gap-3">
                <span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-medium">Low Carb</span>
                <span><strong>Low Carb:</strong> Contains 20g or less of net carbs per serving</span>
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Spice Levels</h2>
            <p>
              Thai cuisine often includes spicy elements. Our spice scale:
            </p>
            <ul className="list-none pl-0 mt-4 space-y-2">
              <li className="flex items-center gap-3">
                <span className="text-lg">🌶️</span>
                <span><strong>Mild (1):</strong> Very light heat, suitable for most people</span>
              </li>
              <li className="flex items-center gap-3">
                <span className="text-lg">🌶️🌶️</span>
                <span><strong>Medium (2):</strong> Noticeable heat, our most popular level</span>
              </li>
              <li className="flex items-center gap-3">
                <span className="text-lg">🌶️🌶️🌶️</span>
                <span><strong>Hot (3):</strong> Spicy, for those who enjoy heat</span>
              </li>
              <li className="flex items-center gap-3">
                <span className="text-lg">🌶️🌶️🌶️🌶️</span>
                <span><strong>Thai Hot (4):</strong> Very spicy, authentic Thai heat levels</span>
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Cross-Contamination Statement</h2>
            <p>
              While we take precautions to prevent cross-contamination, please be aware:
            </p>
            <ul className="list-disc pl-6 mt-2 space-y-1">
              <li>All meals are prepared in a shared kitchen facility</li>
              <li>We use common equipment for all preparations</li>
              <li>Trace amounts of allergens may be present in any meal</li>
              <li>We cannot guarantee allergen-free meals</li>
            </ul>
            <p className="mt-4">
              <strong>If you have a severe or life-threatening allergy, we recommend
              not ordering from our service.</strong>
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Our Precautions</h2>
            <p>
              To minimize cross-contamination risks, we follow these practices:
            </p>
            <ul className="list-disc pl-6 mt-2 space-y-1">
              <li>Color-coded cutting boards for different food types</li>
              <li>Separate storage for allergen-containing ingredients</li>
              <li>Staff training on allergen awareness</li>
              <li>Thorough cleaning between meal preparations</li>
              <li>Clear labeling of all ingredients in our inventory</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Food Safety Practices</h2>

            <h3 className="text-xl font-medium mt-4 mb-2">Temperature Control</h3>
            <ul className="list-disc pl-6 mt-2 space-y-1">
              <li>All meals are cooked to safe internal temperatures</li>
              <li>Rapid cooling protocols after cooking</li>
              <li>Refrigerated storage at 4°C (40°F) or below</li>
              <li>Insulated delivery containers with ice packs</li>
            </ul>

            <h3 className="text-xl font-medium mt-4 mb-2">Freshness Standards</h3>
            <ul className="list-disc pl-6 mt-2 space-y-1">
              <li>Meals prepared fresh on Saturday for Sunday delivery</li>
              <li>Best consumed within 5 days of delivery</li>
              <li>Freeze within 3 days for extended storage (up to 2 weeks)</li>
              <li>All meals labeled with preparation date</li>
            </ul>

            <h3 className="text-xl font-medium mt-4 mb-2">Reheating Instructions</h3>
            <ul className="list-disc pl-6 mt-2 space-y-1">
              <li><strong>Microwave:</strong> Remove lid, heat 2-3 minutes, stir, heat additional 1-2 minutes</li>
              <li><strong>Oven:</strong> Transfer to oven-safe dish, cover with foil, heat at 350°F for 15-20 minutes</li>
              <li><strong>Stovetop:</strong> Transfer to pan, heat over medium heat for 5-7 minutes, stirring occasionally</li>
              <li>Ensure food reaches internal temperature of 74°C (165°F)</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Nutritional Information</h2>
            <p>
              Each meal on our menu includes detailed nutritional information:
            </p>
            <ul className="list-disc pl-6 mt-2 space-y-1">
              <li>Calories</li>
              <li>Protein (g)</li>
              <li>Carbohydrates (g)</li>
              <li>Fat (g)</li>
              <li>Fiber (g)</li>
              <li>Sodium (mg)</li>
              <li>Sugar (g)</li>
            </ul>
            <p className="mt-2">
              Nutritional values are estimates and may vary slightly based on ingredient variations.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Ingredient Sourcing</h2>
            <p>
              We prioritize quality ingredients:
            </p>
            <ul className="list-disc pl-6 mt-2 space-y-1">
              <li>Proteins sourced from Canadian suppliers when available</li>
              <li>Fresh vegetables from local Ontario farms (seasonal)</li>
              <li>Authentic Thai ingredients imported for traditional recipes</li>
              <li>No MSG added to our recipes</li>
              <li>No artificial preservatives</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Special Dietary Requests</h2>
            <p>
              While we cannot accommodate custom modifications to meals, we offer:
            </p>
            <ul className="list-disc pl-6 mt-2 space-y-1">
              <li>Varied menu with gluten-free and dairy-free options each week</li>
              <li>Clear allergen labeling on all menu items</li>
              <li>Full ingredient lists available upon request</li>
            </ul>
            <p className="mt-2">
              For specific dietary questions, please contact us before ordering.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Reporting Concerns</h2>
            <p>
              If you experience an allergic reaction or have food safety concerns:
            </p>
            <ol className="list-decimal pl-6 mt-2 space-y-1">
              <li>Seek medical attention if needed</li>
              <li>Contact us immediately at support@welamealprep.ca</li>
              <li>Retain the meal container and any remaining food</li>
              <li>Note the meal name, order number, and symptoms</li>
            </ol>
            <p className="mt-4">
              We take all reports seriously and will investigate promptly.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Contact Us</h2>
            <p>
              For allergen-related questions or concerns:
            </p>
            <p className="mt-2">
              <strong>Email:</strong> support@welamealprep.ca<br />
              <strong>Subject Line:</strong> Allergen Inquiry - [Your Name]
            </p>
            <p className="mt-4 text-sm text-gray-500">
              This information is provided to help you make informed decisions. It does not
              constitute medical advice. Please consult your healthcare provider for
              guidance on managing food allergies.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}
