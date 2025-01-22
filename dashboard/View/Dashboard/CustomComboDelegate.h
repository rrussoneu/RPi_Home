//
// Created by Raphael Russo on 1/21/25.
//

#ifndef CUSTOM_COMBO_DELEGATE_H
#define CUSTOM_COMBO_DELEGATE_H

#include <QStyledItemDelegate>
#include <QPainter>

#include <QProxyStyle>
#include <QStyleOption>

class ComboBoxStyle : public QProxyStyle {
public:
    explicit ComboBoxStyle(QStyle* style = nullptr) : QProxyStyle(style) {}

    int pixelMetric(PixelMetric metric, const QStyleOption* option = nullptr,
                    const QWidget* widget = nullptr) const override {
        // Remove the popup window margins
        if (metric == PM_MenuVMargin || metric == PM_MenuPanelWidth
            || metric == PM_MenuHMargin || metric == PM_MenuDesktopFrameWidth) {
            return 0;
        }
        return QProxyStyle::pixelMetric(metric, option, widget);
    }
};

class CustomComboDelegate : public QStyledItemDelegate {
Q_OBJECT
public:
    explicit CustomComboDelegate(QObject* parent = nullptr) : QStyledItemDelegate(parent) {}

    void paint(QPainter* painter, const QStyleOptionViewItem& option,
               const QModelIndex& index) const override {
        QStyleOptionViewItem opt = option;
        initStyleOption(&opt, index);

        // Remove any spacing at top/bottom of the popup
        if (index.row() == 0) {
            opt.rect.setTop(0);
        }

        painter->save();

        // Draw background
        if (opt.state & QStyle::State_MouseOver) {
            painter->fillRect(opt.rect, QColor("#2f334d"));
        } else if (opt.state & QStyle::State_Selected) {
            painter->fillRect(opt.rect, QColor("#7aa2f7"));
        }

        // Draw text
        if (opt.state & QStyle::State_Selected) {
            painter->setPen(QColor("#1a1b26"));
        } else {
            painter->setPen(QColor("#c0caf5"));
        }

        painter->drawText(opt.rect.adjusted(12, 0, -12, 0),
                          Qt::AlignVCenter | Qt::AlignLeft,
                          index.data().toString());

        painter->restore();
    }

    QSize sizeHint(const QStyleOptionViewItem& option,
                   const QModelIndex& index) const override {
        return QSize(200, 36); // Fixed height for items
    }
};

#endif // CUSTOM_COMBO_DELEGATE_H