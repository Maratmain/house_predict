import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater, 
    CommandHandler, 
    CallbackQueryHandler, 
    MessageHandler, 
    Filters, 
    ConversationHandler, 
    CallbackContext
)
import pickle
from datetime import datetime
import pandas as pd

with open('linear_regression_model.pkl', 'rb') as f:
    model = pickle.load(f)
print("Model expects features:", model.feature_names_in_)

DATE, BEDROOMS, BATHROOMS, SQFT_LIVING, SQFT_LOT, FLOORS, WATERFRONT, VIEW, CONDITION, SQFT_ABOVE, SQFT_BASEMENT, LAST_CHANGED = range(12)

def start(update: Update, context: CallbackContext):
    user = update.effective_user
    message = f"Hello, {user.first_name}! Here's a preview of the data:"
    
    keyboard = [
        [InlineKeyboardButton("📊 Explore Data", callback_data='explore')],
        [InlineKeyboardButton("💰 Estimate Price", callback_data='estimate')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(message, reply_markup=reply_markup)
    
    preview_image_path = 'plots/preview.png'
    
    if os.path.exists(preview_image_path):
        with open(preview_image_path, 'rb') as photo:
            update.message.reply_photo(photo=photo, caption="📸 Data Preview")
    else:
        update.message.reply_text("⚠️ Preview image not found.")

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == 'explore':
        explore_data(query)
    elif query.data == 'estimate':
        return estimate_price_start(update, context)

def explore_data(query):
    plots = [
        ('plots/bathrooms.png', '🛁 Price Distribution by Number of Bathrooms',
         "This boxplot displays the distribution of house prices based on the number of bathrooms. It helps identify how the number of bathrooms affects the overall price."),
        ('plots/bedrooms.png', '🛏️ Price Distribution by Number of Bedrooms',
         "This boxplot illustrates the distribution of house prices based on the number of bedrooms. It helps identify how the number of bedrooms affects the overall price."),
        ('plots/heatmap.png', '🔗 Correlation Heatmap',
         "The heatmap displays the correlation coefficients between different features and the target variable (price). It helps in understanding which features are most strongly associated with the house price."),
        ('plots/hypothesis.png', '📊 Hypothesis Validation',
         "This plot validates the hypothesis that houses with the same number of bedrooms but with waterfront have a higher median price across cities."),
        ('plots/overall.png', '📈 Overall Price Trends',
         "This plot shows the overall trend of house prices against various features, providing a comprehensive view of the data."),
        ('plots/price.png', '💵 Price Distribution',
         "This histogram shows the distribution of house prices in the dataset. It highlights the frequency of houses within specific price ranges."),
        ('plots/views.png', '👀 Price Distribution by Views Rated',
         "This boxplot shows how house prices are distributed across different view ratings. Each box represents the median, quartiles, and potential outliers for the price within each view category."),
        ('plots/actualvspredicted.png', '🔮 Predicted vs Actual Prices',
         "This scatter plot visualizes the relationship between the actual house prices and the prices predicted by the linear regression model. The red diagonal line represents perfect predictions.")
    ]

    for plot_path, title, description in plots:
        if os.path.exists(plot_path):
            with open(plot_path, 'rb') as f:
                query.message.reply_photo(photo=f, caption=f"*{title}*\n{description}", parse_mode='Markdown')
        else:
            query.message.reply_text(f"📂 Plot {os.path.basename(plot_path)} not found.")

def estimate_price_start(update: Update, context: CallbackContext):
    prompt = (
        "💰 Price Estimation\n\n"
        "Please provide the following details for price estimation:\n\n"
        "1. Date (e.g., 2014-12-09)\n"
        "2. Bedrooms (e.g., 3)\n"
        "3. Bathrooms (e.g., 2.5)\n"
        "4. Sqft Living (e.g., 2000)\n"
        "5. Sqft Lot (e.g., 5000)\n"
        "6. Floors (e.g., 1)\n"
        "7. Waterfront (0 for No, 1 for Yes)\n"
        "8. View (e.g., 4)\n"
        "9. Condition (e.g., 3)\n"
        "10. Sqft Above (e.g., 1800)\n"
        "11. Sqft Basement (e.g., 200)\n"
        "12. Last Changed (e.g., 2000)\n\n"
        "📝 Please enter the values one by one as prompted."
    )
    update.callback_query.message.reply_text(prompt)
    return DATE

def estimate_price_date(update: Update, context: CallbackContext):
    user_input = update.message.text
    try:
        date_obj = datetime.strptime(user_input.strip(), '%Y-%m-%d')
        date_numeric = float(date_obj.timestamp())
        context.user_data['date'] = date_numeric
        
        update.message.reply_text("🔢 Please enter the number of bedrooms (e.g., 3):")
        return BEDROOMS
    except ValueError:
        update.message.reply_text("❌ Invalid date format. Please enter the date in YYYY-MM-DD format (e.g., 2023-12-09).")
        return DATE

def estimate_price_bedrooms(update: Update, context: CallbackContext):
    try:
        bedrooms = float(update.message.text)
        context.user_data['bedrooms'] = bedrooms
        update.message.reply_text("🔢 Please enter the number of bathrooms (e.g., 2.5):")
        return BATHROOMS
    except ValueError:
        update.message.reply_text("❌ Invalid input. Please enter a numerical value for bedrooms.")
        return BEDROOMS

def estimate_price_bathrooms(update: Update, context: CallbackContext):
    try:
        bathrooms = float(update.message.text)
        context.user_data['bathrooms'] = bathrooms
        update.message.reply_text("🏠 Please enter the sqft living area (e.g., 2000):")
        return SQFT_LIVING
    except ValueError:
        update.message.reply_text("❌ Invalid input. Please enter a numerical value for bathrooms.")
        return BATHROOMS

def estimate_price_sqft_living(update: Update, context: CallbackContext):
    try:
        sqft_living = int(update.message.text)
        context.user_data['sqft_living'] = sqft_living
        update.message.reply_text("📐 Please enter the sqft lot area (e.g., 5000):")
        return SQFT_LOT
    except ValueError:
        update.message.reply_text("❌ Invalid input. Please enter a numerical value for sqft living.")
        return SQFT_LIVING

def estimate_price_sqft_lot(update: Update, context: CallbackContext):
    try:
        sqft_lot = int(update.message.text)
        context.user_data['sqft_lot'] = sqft_lot
        update.message.reply_text("🏡 Please enter the number of floors (e.g., 1):")
        return FLOORS
    except ValueError:
        update.message.reply_text("❌ Invalid input. Please enter a numerical value for sqft lot.")
        return SQFT_LOT

def estimate_price_floors(update: Update, context: CallbackContext):
    try:
        floors = float(update.message.text)
        context.user_data['floors'] = floors
        update.message.reply_text("🌊 Is the house waterfront? (0 for No, 1 for Yes):")
        return WATERFRONT
    except ValueError:
        update.message.reply_text("❌ Invalid input. Please enter a numerical value for floors.")
        return FLOORS

def estimate_price_waterfront(update: Update, context: CallbackContext):
    try:
        waterfront = int(update.message.text)
        if waterfront not in [0, 1]:
            raise ValueError
        context.user_data['waterfront'] = waterfront
        update.message.reply_text("👀 Please enter the view rating (e.g., 4):")
        return VIEW
    except ValueError:
        update.message.reply_text("❌ Invalid input. Please enter 0 for No or 1 for Yes.")
        return WATERFRONT

def estimate_price_view(update: Update, context: CallbackContext):
    try:
        view = int(update.message.text)
        context.user_data['view'] = view
        update.message.reply_text("🔧 Please enter the condition rating (e.g., 3):")
        return CONDITION
    except ValueError:
        update.message.reply_text("❌ Invalid input. Please enter a numerical value for view rating.")
        return VIEW

def estimate_price_condition(update: Update, context: CallbackContext):
    try:
        condition = int(update.message.text)
        context.user_data['condition'] = condition
        update.message.reply_text("📏 Please enter the sqft above area (e.g., 1800):")
        return SQFT_ABOVE
    except ValueError:
        update.message.reply_text("❌ Invalid input. Please enter a numerical value for condition rating.")
        return CONDITION

def estimate_price_sqft_above(update: Update, context: CallbackContext):
    try:
        sqft_above = int(update.message.text)
        context.user_data['sqft_above'] = sqft_above
        update.message.reply_text("🏠 Please enter the sqft basement area (e.g., 200):")
        return SQFT_BASEMENT
    except ValueError:
        update.message.reply_text("❌ Invalid input. Please enter a numerical value for sqft above area.")
        return SQFT_ABOVE

def estimate_price_sqft_basement(update: Update, context: CallbackContext):
    try:
        sqft_basement = int(update.message.text)
        context.user_data['sqft_basement'] = sqft_basement
        update.message.reply_text("🔢 Please enter when it was renovated last time(if hasn't, write the years when it was built) (e.g., 2000):")
        return LAST_CHANGED
    except ValueError:
        update.message.reply_text("❌ Invalid input. Please enter a numerical value for sqft basement.")
        return SQFT_BASEMENT

def estimate_price_last_changed(update: Update, context: CallbackContext):
    try:
        last_changed = int(update.message.text)
        context.user_data['last_changed'] = last_changed
        input_data = pd.DataFrame([[
            context.user_data['date'],
            context.user_data['bedrooms'],
            context.user_data['bathrooms'],
            context.user_data['sqft_living'],
            context.user_data['sqft_lot'],
            context.user_data['floors'],
            context.user_data['waterfront'],
            context.user_data['view'],
            context.user_data['condition'],
            context.user_data['sqft_above'],
            context.user_data['sqft_basement'],
            context.user_data['last_changed']
        ]], columns=[
            'date', 'bedrooms', 'bathrooms', 'sqft_living',
            'sqft_lot', 'floors', 'waterfront', 'view', 'condition',
            'sqft_above', 'sqft_basement', 'last_changed'
        ])
        print(input_data)

        # Предсказание цены
        predicted_price = float(model.predict(input_data))
        response = f"🏠 *Estimated Price*: ${predicted_price:,.2f}"
        update.message.reply_text(response, parse_mode='Markdown')

        return ConversationHandler.END

    except ValueError:
        update.message.reply_text("❌ Invalid input. Please enter a numerical value for last changed.")
        return LAST_CHANGED

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("🛑 Estimation cancelled. You can start again by sending /start.")
    return ConversationHandler.END

def handle_message(update: Update, context: CallbackContext):
    update.message.reply_text("ℹ️ Please use /start to begin.")

def main():
    TELEGRAM_TOKEN = '7880031384:AAHRPFg25GJfYpwBaBLw6uktLv-6chX23i8' 

    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button)],
        states={
            DATE: [MessageHandler(Filters.text & ~Filters.command, estimate_price_date)],
            BEDROOMS: [MessageHandler(Filters.text & ~Filters.command, estimate_price_bedrooms)],
            BATHROOMS: [MessageHandler(Filters.text & ~Filters.command, estimate_price_bathrooms)],
            SQFT_LIVING: [MessageHandler(Filters.text & ~Filters.command, estimate_price_sqft_living)],
            SQFT_LOT: [MessageHandler(Filters.text & ~Filters.command, estimate_price_sqft_lot)],
            FLOORS: [MessageHandler(Filters.text & ~Filters.command, estimate_price_floors)],
            WATERFRONT: [MessageHandler(Filters.text & ~Filters.command, estimate_price_waterfront)],
            VIEW: [MessageHandler(Filters.text & ~Filters.command, estimate_price_view)],
            CONDITION: [MessageHandler(Filters.text & ~Filters.command, estimate_price_condition)],
            SQFT_ABOVE: [MessageHandler(Filters.text & ~Filters.command, estimate_price_sqft_above)],
            SQFT_BASEMENT: [MessageHandler(Filters.text & ~Filters.command, estimate_price_sqft_basement)],
            LAST_CHANGED: [MessageHandler(Filters.text & ~Filters.command, estimate_price_last_changed)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    print("Bot started. Press Ctrl+C to stop.")
    updater.idle()

if __name__ == '__main__':
    main()
