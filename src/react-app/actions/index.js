export const ON_CHANGE_SUBSCRIPTION_CARD = 'ON_CHANGE_SUBSCRIPTION_CARD'
export const onChangeNewGameBoardField = (changedField, index) => {
  return (
    {
      type: ON_CHANGE_SUBSCRIPTION_CARD,
      changedField,
      index,
    }
  )
}